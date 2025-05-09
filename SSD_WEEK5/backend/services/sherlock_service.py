import aiohttp
from typing import Dict, List

class SherlockService:
    def __init__(self):
        pass

    async def search_username(self, username: str) -> Dict:
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
                            'username': username,
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

async def search_username(username: str) -> Dict[str, List[Dict]]:
    """
    Search for a username across various social media platforms using Sherlock API
    """
    service = SherlockService()
    return await service.search_username(username) 