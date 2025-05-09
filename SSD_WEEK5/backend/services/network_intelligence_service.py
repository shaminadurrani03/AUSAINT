import requests
import whois
import dns.resolver
import logging
from typing import Dict, List, Any, Optional
import socket
import json
import traceback
import os
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkIntelligenceService:
    def __init__(self):
        # Free APIs and services
        self.ip_api_url = "http://ip-api.com/json/"  # Free IP geolocation API
        self.hackertarget_api = "https://api.hackertarget.com/"
        self.ipinfo_token = os.getenv("IPINFO_TOKEN")
        
    async def lookup_ip(self, ip: str) -> Dict[str, Any]:
        """
        Lookup IP geolocation information using multiple sources
        """
        try:
            logger.info(f"Looking up IP information for {ip}")
            
            # Validate IP address format
            try:
                socket.inet_aton(ip)
            except socket.error:
                raise ValueError("Invalid IP address format")
            
            # Try ip-api.com first
            try:
                response = requests.get(
                    f"{self.ip_api_url}{ip}",
                    timeout=5
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "success":
                    result = {
                        "ip": ip,
                        "city": data.get("city"),
                        "region": data.get("regionName"),
                        "country": data.get("country"),
                        "location": f"{data.get('lat')},{data.get('lon')}",
                        "org": data.get("org"),
                        "asn": data.get("as"),
                        "isp": data.get("isp"),
                        "timezone": data.get("timezone")
                    }
                else:
                    raise Exception("IP lookup failed")
            except Exception as e:
                logger.warning(f"ip-api.com lookup failed: {str(e)}")
                # Fallback to basic information
                result = {
                    "ip": ip,
                    "error": "Detailed lookup failed, showing basic information"
                }
            
            # Get hostname using reverse DNS
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                result["hostname"] = hostname
            except:
                result["hostname"] = None
            
            logger.info(f"Successfully retrieved IP information for {ip}")
            return result
            
        except Exception as e:
            logger.error(f"Error looking up IP {ip}: {str(e)}")
            raise Exception(f"Failed to lookup IP information: {str(e)}")

    async def lookup_whois(self, domain: str) -> Dict[str, Any]:
        """
        Get WHOIS information using multiple methods
        """
        try:
            logger.info(f"Looking up WHOIS information for {domain}")
            
            # Try python-whois first
            try:
                w = whois.whois(domain)
                result = {
                    "domain_name": w.domain_name,
                    "registrar": w.registrar,
                    "creation_date": str(w.creation_date) if w.creation_date else None,
                    "expiration_date": str(w.expiration_date) if w.expiration_date else None,
                    "updated_date": str(w.updated_date) if w.updated_date else None,
                    "name_servers": w.name_servers if isinstance(w.name_servers, list) else [w.name_servers] if w.name_servers else [],
                    "status": w.status if isinstance(w.status, list) else [w.status] if w.status else [],
                    "emails": w.emails if isinstance(w.emails, list) else [w.emails] if w.emails else []
                }
            except Exception as whois_error:
                logger.warning(f"python-whois failed: {str(whois_error)}")
                # Fallback to HackerTarget API
                try:
                    response = requests.get(
                        f"{self.hackertarget_api}whois/?q={domain}",
                        timeout=10
                    )
                    response.raise_for_status()
                    result = {
                        "domain_name": domain,
                        "raw_whois": response.text
                    }
                except Exception as api_error:
                    logger.error(f"HackerTarget API fallback failed: {str(api_error)}")
                    result = {
                        "domain_name": domain,
                        "error": "WHOIS lookup failed"
                    }
            
            logger.info(f"Successfully retrieved WHOIS information for {domain}")
            return result
            
        except Exception as e:
            logger.error(f"Error looking up WHOIS for {domain}: {str(e)}")
            raise Exception(f"Failed to get WHOIS information: {str(e)}")

    async def find_subdomains(self, domain: str) -> Dict[str, Any]:
        """
        Find subdomains using multiple methods with rate limiting
        """
        try:
            logger.info(f"Finding subdomains for {domain}")
            
            subdomains = set()
            
            # Method 1: Try common subdomain prefixes
            common_prefixes = ['www', 'mail', 'ftp', 'smtp', 'pop', 'ns1', 'ns2', 'admin', 'blog', 'shop', 'store', 'api', 'dev', 'test', 'stage', 'prod']
            
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '8.8.4.4']
            resolver.timeout = 2
            resolver.lifetime = 2
            
            # Use ThreadPoolExecutor for parallel DNS lookups
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_prefix = {
                    executor.submit(self._check_subdomain, f"{prefix}.{domain}", resolver): prefix
                    for prefix in common_prefixes
                }
                
                for future in as_completed(future_to_prefix):
                    try:
                        subdomain = future.result()
                        if subdomain:
                            subdomains.add(subdomain)
                    except Exception as e:
                        logger.warning(f"Subdomain check failed: {str(e)}")
            
            # Method 2: Try HackerTarget API
            try:
                response = requests.get(
                    f"{self.hackertarget_api}hostsearch/?q={domain}",
                    timeout=10
                )
                response.raise_for_status()
                
                for line in response.text.splitlines():
                    if line.strip():
                        subdomain = line.split(',')[0]
                        subdomains.add(subdomain)
            except Exception as api_error:
                logger.warning(f"HackerTarget API failed: {str(api_error)}")
            
            result = {
                "domain": domain,
                "total_subdomains": len(subdomains),
                "subdomains": sorted(list(subdomains))
            }
            
            logger.info(f"Successfully found {len(subdomains)} subdomains for {domain}")
            return result
            
        except Exception as e:
            logger.error(f"Error finding subdomains for {domain}: {str(e)}")
            raise Exception(f"Failed to find subdomains: {str(e)}")

    async def _check_subdomain(self, subdomain: str, resolver: dns.resolver.Resolver) -> Optional[str]:
        """
        Check if a subdomain exists
        """
        try:
            resolver.resolve(subdomain, 'A')
            return subdomain
        except:
            return None

    async def lookup_dns(self, domain: str, record_type: str = 'A') -> Dict[str, Any]:
        """
        Lookup DNS records using dns.resolver with fallback to HackerTarget API
        """
        try:
            logger.info(f"Looking up {record_type} records for {domain}")
            
            records = []
            
            # Try using dns.resolver first
            try:
                resolver = dns.resolver.Resolver()
                resolver.timeout = 5
                resolver.lifetime = 5
                resolver.nameservers = ['8.8.8.8', '8.8.4.4']
                
                answers = resolver.resolve(domain, record_type)
                for rdata in answers:
                    records.append({
                        "name": domain,
                        "type": record_type,
                        "value": str(rdata)
                    })
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException) as e:
                logger.warning(f"DNS resolver failed for {domain}: {str(e)}")
                
                # Fallback to HackerTarget API
                try:
                    response = requests.get(
                        f"{self.hackertarget_api}dnslookup/?q={domain}",
                        timeout=10
                    )
                    response.raise_for_status()
                    
                    for line in response.text.splitlines():
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 3 and parts[1] == record_type:
                                records.append({
                                    "name": parts[0],
                                    "type": parts[1],
                                    "value": " ".join(parts[2:])
                                })
                except Exception as api_error:
                    logger.error(f"HackerTarget API fallback failed: {str(api_error)}")
            
            result = {
                "domain": domain,
                "record_type": record_type,
                "total_records": len(records),
                "records": records
            }
            
            logger.info(f"Successfully retrieved {len(records)} {record_type} records for {domain}")
            return result
            
        except Exception as e:
            logger.error(f"Error looking up DNS records for {domain}: {str(e)}")
            raise Exception(f"Failed to lookup DNS records: {str(e)}")

    async def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """
        Perform comprehensive domain analysis
        """
        try:
            logger.info(f"Starting comprehensive analysis for {domain}")
            
            # Get WHOIS information
            whois_info = await self.lookup_whois(domain)
            
            # Find subdomains
            subdomains_info = await self.find_subdomains(domain)
            
            # Get DNS records
            dns_records = {}
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT']
            
            for record_type in record_types:
                try:
                    dns_records[record_type] = await self.lookup_dns(domain, record_type)
                except Exception as e:
                    logger.warning(f"Failed to get {record_type} records: {str(e)}")
                    dns_records[record_type] = {
                        "domain": domain,
                        "record_type": record_type,
                        "total_records": 0,
                        "records": []
                    }
            
            result = {
                "domain": domain,
                "whois": whois_info,
                "subdomains": subdomains_info,
                "dns_records": dns_records
            }
            
            logger.info(f"Successfully completed analysis for {domain}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing domain {domain}: {str(e)}")
            raise Exception(f"Failed to analyze domain: {str(e)}") 