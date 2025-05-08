import sys
import os
from pathlib import Path
import asyncio
from typing import Dict, List

# Add Sherlock to Python path
sherlock_path = Path(__file__).parent.parent / 'api' / 'sherlock'
sys.path.append(str(sherlock_path))

from sherlock_project.sherlock import sherlock
from sherlock_project.notify import QueryNotifyPrint
from sherlock_project.sites import SitesInformation

class SherlockService:
    def __init__(self):
        sites_info = SitesInformation()
        self.sites = sites_info.sites
        self.notify = QueryNotifyPrint()

    async def search_username(self, username: str) -> Dict:
        """
        Search for a username across various social media platforms using Sherlock
        """
        try:
            # Run Sherlock search
            results = sherlock(
                username=username,
                site_data=self.sites,
                query_notify=self.notify,
                timeout=30
            )
            
            # Process results
            found_accounts = []
            for site, result in results.items():
                if result.get('status') == 'Claimed':
                    found_accounts.append({
                        'platform': site,
                        'url': result.get('url_user'),
                        'username': username,
                        'status': 'found'
                    })
            
            return {
                'success': True,
                'username': username,
                'accounts_found': len(found_accounts),
                'accounts': found_accounts
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

async def search_username(username: str) -> Dict[str, List[Dict]]:
    """
    Search for a username across various social media platforms using Sherlock API
    """
    async with aiohttp.ClientSession() as session:
        # Sherlock API endpoint
        url = f"https://sherlock-project.github.io/api/{username}"
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'success': True,
                        'results': data
                    }
                else:
                    return {
                        'success': False,
                        'error': f'API returned status code {response.status}'
                    }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 