import aiohttp
import logging
from typing import Dict, List
import json
import re
import traceback
import ssl
import certifi
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CredentialLeakService:
    def __init__(self):
        self.base_url = "https://breachdirectory.org/api"
        # Create SSL context with certificate verification
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        logger.info("Initialized CredentialLeakService")
        
        # Sample breach data for testing
        self.sample_breaches = [
            {
                'name': 'LinkedIn',
                'title': 'LinkedIn Data Breach 2012',
                'date': '2012-06-05',
                'description': 'In 2012, LinkedIn suffered a data breach that exposed 117 million email and password combinations.',
                'data_classes': ['Email addresses', 'Passwords', 'Usernames']
            },
            {
                'name': 'Adobe',
                'title': 'Adobe Data Breach 2013',
                'date': '2013-10-04',
                'description': 'In 2013, Adobe suffered a data breach that exposed 153 million user records.',
                'data_classes': ['Email addresses', 'Passwords', 'Usernames', 'Credit card information']
            },
            {
                'name': 'Dropbox',
                'title': 'Dropbox Data Breach 2012',
                'date': '2012-07-01',
                'description': 'In 2012, Dropbox suffered a data breach that exposed 68 million user records.',
                'data_classes': ['Email addresses', 'Passwords', 'Usernames']
            }
        ]

    async def check_credential_leaks(self, email: str) -> Dict:
        """
        Check if an email has been involved in any data breaches
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

            # For testing purposes, randomly select breaches
            # In a real implementation, this would be replaced with actual API calls
            num_breaches = random.randint(0, len(self.sample_breaches))
            selected_breaches = random.sample(self.sample_breaches, num_breaches) if num_breaches > 0 else []

            result = {
                'success': True,
                'email': email,
                'breaches': selected_breaches,
                'pastes': [],  # No paste information for now
                'total_breaches': len(selected_breaches),
                'total_pastes': 0,
                'risk_level': self._calculate_risk_level(len(selected_breaches))
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
        Check if a password has been leaked
        """
        try:
            logger.info("Checking password leak")
            
            if not password or not isinstance(password, str):
                logger.error("Invalid password provided")
                return {
                    'success': False,
                    'error': 'Invalid password provided'
                }

            # For testing purposes, randomly determine if password is leaked
            is_leaked = random.choice([True, False])
            times_leaked = random.randint(1, 5) if is_leaked else 0

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