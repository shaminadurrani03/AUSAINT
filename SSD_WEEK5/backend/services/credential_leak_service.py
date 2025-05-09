import aiohttp
import logging
from typing import Dict, List
import json
import re
import traceback
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CredentialLeakService:
    def __init__(self):
        self.base_url = "https://leakcheck.io/api"
        self.api_key = os.getenv("LEAKCHECK_API_KEY", "your_api_key_here")  # Replace with your actual API key
        logger.info("Initialized CredentialLeakService")

    async def check_credential_leaks(self, email: str) -> Dict:
        """
        Check if an email has been involved in any data breaches using LeakCheck.io
        """
        try:
            logger.info(f"Checking credential leaks for email: {email}")
            
            if not email or not isinstance(email, str):
                logger.error("Invalid email provided")
                return {
                    'success': False,
                    'error': 'Invalid email provided'
                }

            # Validate email format
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                logger.error(f"Invalid email format: {email}")
                return {
                    'success': False,
                    'error': 'Invalid email format'
                }

            logger.info(f"Making request to LeakCheck API for email: {email}")
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/check"
                params = {
                    'key': self.api_key,
                    'check': email,
                    'type': 'email'
                }
                logger.info(f"Request URL: {url}")
                
                async with session.get(url, params=params) as response:
                    response_text = await response.text()
                    logger.info(f"API Response Status: {response.status}")
                    logger.info(f"API Response: {response_text}")
                    
                    if response.status != 200:
                        logger.error(f"LeakCheck API error: {response.status} - {response_text}")
                        return {
                            'success': False,
                            'error': f"API request failed: {response.status}"
                        }

                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse API response: {e}")
                        return {
                            'success': False,
                            'error': 'Invalid API response format'
                        }
                    
                    # Process the results
                    breaches = []
                    if data.get('success'):
                        for source in data.get('sources', []):
                            breaches.append({
                                'name': source,
                                'title': f"Leak from {source}",
                                'breach_date': 'Unknown',  # LeakCheck doesn't provide dates
                                'description': f"Found in {source} data leak",
                                'data_classes': ['Email addresses', 'Passwords']
                            })

                    result = {
                        'success': True,
                        'email': email,
                        'breaches': breaches,
                        'pastes': [],  # LeakCheck doesn't provide paste information
                        'total_breaches': len(breaches),
                        'total_pastes': 0,
                        'risk_level': self._calculate_risk_level(len(breaches))
                    }
                    
                    logger.info(f"Successfully processed results: {json.dumps(result)}")
                    return result

        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error checking credential leaks: {str(e)}\n{error_details}")
            return {
                'success': False,
                'error': str(e),
                'details': error_details
            }

    def _calculate_risk_level(self, breach_count: int) -> str:
        """
        Calculate risk level based on number of breaches
        """
        if breach_count == 0:
            return 'low'
        elif breach_count <= 2:
            return 'medium'
        else:
            return 'high'

    async def check_password_leak(self, password: str) -> Dict:
        """
        Check if a password has been leaked using LeakCheck.io
        """
        try:
            logger.info("Checking password leak")
            
            if not password or not isinstance(password, str):
                logger.error("Invalid password provided")
                return {
                    'success': False,
                    'error': 'Invalid password provided'
                }

            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/check"
                params = {
                    'key': self.api_key,
                    'check': password,
                    'type': 'password'
                }
                logger.info(f"Request URL: {url}")
                
                async with session.get(url, params=params) as response:
                    response_text = await response.text()
                    logger.info(f"API Response Status: {response.status}")
                    logger.info(f"API Response: {response_text}")
                    
                    if response.status != 200:
                        logger.error(f"LeakCheck API error: {response.status} - {response_text}")
                        return {
                            'success': False,
                            'error': f"API request failed: {response.status}"
                        }

                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse API response: {e}")
                        return {
                            'success': False,
                            'error': 'Invalid API response format'
                        }

                    is_leaked = data.get('success', False) and len(data.get('sources', [])) > 0
                    times_leaked = len(data.get('sources', []))

                    result = {
                        'success': True,
                        'leaked': is_leaked,
                        'times_leaked': times_leaked,
                        'risk_level': 'high' if is_leaked else 'low'
                    }
                    
                    logger.info(f"Successfully processed password results: {json.dumps(result)}")
                    return result

        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error checking password leak: {str(e)}\n{error_details}")
            return {
                'success': False,
                'error': str(e),
                'details': error_details
            } 