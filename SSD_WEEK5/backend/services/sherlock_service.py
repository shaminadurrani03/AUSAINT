import asyncio
from typing import Dict, List
import subprocess
import json
import os
import sys

# Add the Sherlock path to Python path
SHERLOCK_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api', 'sherlock')
sys.path.append(SHERLOCK_PATH)

class SherlockService:
    def __init__(self):
        pass

    async def search_username(self, username: str) -> Dict:
        """
        Search for a username across various social media platforms using Sherlock
        """
        try:
            # Run Sherlock as a subprocess
            process = await asyncio.create_subprocess_exec(
                'python3',
                os.path.join(SHERLOCK_PATH, 'sherlock'),
                username,
                '--timeout', '10',
                '--print-found',
                '--json',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Sherlock failed: {stderr.decode()}")

            # Parse the output
            output = stdout.decode()
            results = {}
            for line in output.split('\n'):
                if line.startswith('[+]'):
                    # Extract site name and URL
                    parts = line.split()
                    if len(parts) >= 3:
                        site = parts[1]
                        url = parts[2]
                        results[site] = {'exists': True, 'url': url}

            # Process results
            found_accounts = []
            for site, data in results.items():
                if data['exists']:
                    found_accounts.append({
                        'name': site,
                        'url': data['url'],
                        'category': self._get_category(site)
                    })
            
            return {
                'success': True,
                'username': username,
                'results': found_accounts
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _get_category(self, site: str) -> str:
        """
        Categorize the social media platform
        """
        categories = {
            'GitHub': 'tech',
            'GitLab': 'tech',
            'Bitbucket': 'tech',
            'Twitter': 'social',
            'Facebook': 'social',
            'Instagram': 'social',
            'LinkedIn': 'professional',
            'Reddit': 'forum',
            'YouTube': 'media',
            'TikTok': 'social',
            'Pinterest': 'social',
            'Medium': 'blog',
            'Dev.to': 'tech',
            'Stack Overflow': 'tech',
            'Quora': 'forum',
            'Steam': 'gaming',
            'Twitch': 'gaming',
            'Discord': 'social',
            'Spotify': 'media',
            'SoundCloud': 'media'
        }
        return categories.get(site, 'other')

async def search_username(username: str) -> Dict[str, List[Dict]]:
    """
    Search for a username across various social media platforms using Sherlock
    """
    service = SherlockService()
    return await service.search_username(username) 