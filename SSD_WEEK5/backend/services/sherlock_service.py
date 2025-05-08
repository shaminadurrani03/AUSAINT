import sys
import os
from pathlib import Path
import asyncio
import aiohttp
import json
from typing import Dict, List

# Add Sherlock to Python path
sherlock_path = Path(__file__).parent.parent / 'api' / 'sherlock'
sys.path.append(str(sherlock_path))

from sherlock_project.sherlock import Sherlock
from sherlock_project.result import QueryStatus

class SherlockService:
    def __init__(self):
        self.sherlock = Sherlock()

    async def search_username(self, username):
        try:
            # Run Sherlock search
            results = await self.sherlock.hunt(username)
            
            # Process results
            found_accounts = []
            for site, result in results.items():
                if result.status == QueryStatus.CLAIMED:
                    found_accounts.append({
                        'platform': site,
                        'url': result.url,
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