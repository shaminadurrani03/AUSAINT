import requests
import whois
import sublist3r
import logging
from typing import Dict, List, Optional, Union
import json
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkIntelligenceService:
    def __init__(self):
        logger.info("Initialized NetworkIntelligenceService")

    async def lookup_ip(self, ip: str) -> Dict:
        """
        Return geolocation for the IP using ipinfo.io free API
        """
        try:
            logger.info(f"Looking up IP: {ip}")
            resp = requests.get(f"https://ipinfo.io/{ip}/json")
            resp.raise_for_status()
            data = resp.json()
            
            result = {
                "ip": data.get("ip"),
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country"),
                "loc": data.get("loc"),  # latitude,longitude
                "org": data.get("org"),
                "asn": data.get("org").split()[0] if data.get("org") else None,
                "hostname": data.get("hostname"),
                "postal": data.get("postal"),
                "timezone": data.get("timezone")
            }
            
            logger.info(f"Successfully retrieved IP information: {json.dumps(result)}")
            return result

        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error looking up IP: {str(e)}\n{error_details}")
            return {
                'success': False,
                'error': str(e),
                'details': error_details
            }

    async def lookup_whois(self, domain: str) -> Dict:
        """
        Return WHOIS info for a given domain
        """
        try:
            logger.info(f"Looking up WHOIS for domain: {domain}")
            w = whois.whois(domain)
            
            result = {
                "domain_name": w.domain_name,
                "registrar": w.registrar,
                "creation_date": str(w.creation_date) if w.creation_date else None,
                "expiration_date": str(w.expiration_date) if w.expiration_date else None,
                "name_servers": w.name_servers if isinstance(w.name_servers, list) else [w.name_servers] if w.name_servers else [],
                "emails": w.emails if isinstance(w.emails, list) else [w.emails] if w.emails else [],
                "status": w.status if isinstance(w.status, list) else [w.status] if w.status else [],
                "dnssec": w.dnssec
            }
            
            logger.info(f"Successfully retrieved WHOIS information: {json.dumps(result)}")
            return result

        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error looking up WHOIS: {str(e)}\n{error_details}")
            return {
                'success': False,
                'error': str(e),
                'details': error_details
            }

    async def find_subdomains(self, domain: str) -> Dict:
        """
        Return a list of discovered subdomains
        """
        try:
            logger.info(f"Finding subdomains for domain: {domain}")
            subs = sublist3r.main(domain, 40, savefile=None, ports=None, silent=True, verbose=False, enable_bruteforce=False, engines=None)
            
            result = {
                "domain": domain,
                "subdomains": subs,
                "total_subdomains": len(subs)
            }
            
            logger.info(f"Successfully found subdomains: {json.dumps(result)}")
            return result

        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error finding subdomains: {str(e)}\n{error_details}")
            return {
                'success': False,
                'error': str(e),
                'details': error_details
            }

    async def lookup_dns(self, domain: str, record_type: str = "A") -> Dict:
        """
        Query DNS records from HackerTarget
        """
        try:
            logger.info(f"Looking up DNS records for domain: {domain}, type: {record_type}")
            url = f"https://api.hackertarget.com/dnslookup/?q={domain}"
            resp = requests.get(url)
            resp.raise_for_status()
            
            # Parse the response into structured data
            dns_records = []
            for line in resp.text.splitlines():
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        dns_records.append({
                            "name": parts[0],
                            "type": parts[1],
                            "value": " ".join(parts[2:])
                        })
            
            result = {
                "domain": domain,
                "records": dns_records,
                "total_records": len(dns_records)
            }
            
            logger.info(f"Successfully retrieved DNS records: {json.dumps(result)}")
            return result

        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error looking up DNS records: {str(e)}\n{error_details}")
            return {
                'success': False,
                'error': str(e),
                'details': error_details
            }

    async def analyze_domain(self, domain: str) -> Dict:
        """
        Perform comprehensive domain analysis including WHOIS, subdomains, and DNS records
        """
        try:
            logger.info(f"Performing comprehensive analysis for domain: {domain}")
            
            # Gather all information
            whois_info = await self.lookup_whois(domain)
            subdomains = await self.find_subdomains(domain)
            dns_records = await self.lookup_dns(domain)
            
            result = {
                "domain": domain,
                "whois": whois_info,
                "subdomains": subdomains,
                "dns_records": dns_records
            }
            
            logger.info(f"Successfully completed domain analysis: {json.dumps(result)}")
            return result

        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error analyzing domain: {str(e)}\n{error_details}")
            return {
                'success': False,
                'error': str(e),
                'details': error_details
            } 