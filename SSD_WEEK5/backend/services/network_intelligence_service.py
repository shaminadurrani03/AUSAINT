import requests
import whois
import sublist3r
import dns.resolver
import logging
from typing import Dict, List, Any, Optional
import socket
import json
import traceback
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkIntelligenceService:
    def __init__(self):
        self.ipinfo_token = os.getenv('IPINFO_TOKEN', '')  # Get from environment variable
        if not self.ipinfo_token:
            logger.warning("IPINFO_TOKEN not found in environment variables. IP lookup will be limited.")
        self.hackertarget_api = "https://api.hackertarget.com/dnslookup/"
        
    async def lookup_ip(self, ip: str) -> Dict[str, Any]:
        """
        Lookup IP geolocation information using ipinfo.io API
        """
        try:
            logger.info(f"Looking up IP information for {ip}")
            
            # Validate IP address format
            try:
                socket.inet_aton(ip)
            except socket.error:
                raise ValueError("Invalid IP address format")
            
            # Make request to ipinfo.io API
            headers = {}
            if self.ipinfo_token:
                headers["Authorization"] = f"Bearer {self.ipinfo_token}"
            
            response = requests.get(
                f"https://ipinfo.io/{ip}/json",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            result = {
                "ip": data.get("ip"),
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country"),
                "location": data.get("loc"),
                "org": data.get("org"),
                "postal": data.get("postal"),
                "timezone": data.get("timezone")
            }
            
            logger.info(f"Successfully retrieved IP information for {ip}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error looking up IP {ip}: {str(e)}")
            raise Exception(f"Failed to lookup IP information: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error looking up IP {ip}: {str(e)}")
            raise Exception(f"An unexpected error occurred: {str(e)}")

    async def lookup_whois(self, domain: str) -> Dict[str, Any]:
        """
        Get WHOIS information for a domain using python-whois
        """
        try:
            logger.info(f"Looking up WHOIS information for {domain}")
            
            # Get WHOIS information
            w = whois.whois(domain)
            
            # Convert WHOIS data to dictionary
            result = {
                "domain_name": w.domain_name,
                "registrar": w.registrar,
                "creation_date": str(w.creation_date) if w.creation_date else None,
                "expiration_date": str(w.expiration_date) if w.expiration_date else None,
                "updated_date": str(w.updated_date) if w.updated_date else None,
                "name_servers": w.name_servers if isinstance(w.name_servers, list) else [w.name_servers] if w.name_servers else [],
                "status": w.status if isinstance(w.status, list) else [w.status] if w.status else [],
                "emails": w.emails if isinstance(w.emails, list) else [w.emails] if w.emails else [],
                "dnssec": w.dnssec if hasattr(w, 'dnssec') else None
            }
            
            logger.info(f"Successfully retrieved WHOIS information for {domain}")
            return result
            
        except Exception as e:
            logger.error(f"Error looking up WHOIS for {domain}: {str(e)}")
            raise Exception(f"Failed to get WHOIS information: {str(e)}")

    async def find_subdomains(self, domain: str) -> Dict[str, Any]:
        """
        Find subdomains using Sublist3r
        """
        try:
            logger.info(f"Finding subdomains for {domain}")
            
            # Use Sublist3r to enumerate subdomains
            subdomains = sublist3r.main(domain, 40, savefile=None, ports=None, silent=True, verbose=False, 
                                      enable_bruteforce=False, engines=None)
            
            result = {
                "domain": domain,
                "total_subdomains": len(subdomains),
                "subdomains": subdomains
            }
            
            logger.info(f"Successfully found {len(subdomains)} subdomains for {domain}")
            return result
            
        except Exception as e:
            logger.error(f"Error finding subdomains for {domain}: {str(e)}")
            raise Exception(f"Failed to find subdomains: {str(e)}")

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
                
                # Use Google's DNS servers for reliability
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
                        f"https://api.hackertarget.com/dnslookup/?q={domain}",
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
            
            # Get common DNS records
            dns_records = {
                "A": await self.lookup_dns(domain, 'A'),
                "AAAA": await self.lookup_dns(domain, 'AAAA'),
                "MX": await self.lookup_dns(domain, 'MX'),
                "NS": await self.lookup_dns(domain, 'NS'),
                "TXT": await self.lookup_dns(domain, 'TXT')
            }
            
            # Combine all results
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