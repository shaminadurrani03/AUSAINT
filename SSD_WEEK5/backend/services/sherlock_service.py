import asyncio
from typing import Dict, List
from sherlock_project.sherlock import Sherlock

class SherlockService:
    def __init__(self):
        self.sherlock = Sherlock()

    async def search_username(self, username: str) -> Dict:
        """
        Search for a username across various social media platforms using Sherlock
        """
        try:
            # Run Sherlock search
            results = await asyncio.to_thread(
                self.sherlock.hunt,
                username,
                timeout=10,
                no_color=True,
                print_found=True,
                json=True
            )
            
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