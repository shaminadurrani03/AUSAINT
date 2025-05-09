import os
import json
from typing import Dict, Any
import asyncio
from supabase.functions import serve
from sherlock_project.sherlock import Sherlock

async def search_username(username: str) -> Dict[str, Any]:
    """Search for a username across various social media platforms using Sherlock"""
    try:
        sherlock = Sherlock()
        results = await asyncio.to_thread(
            sherlock.hunt,
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
                    'category': get_category(site)
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

def get_category(site: str) -> str:
    """Categorize the social media platform"""
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

async def handle_request(req):
    try:
        # Parse request body
        body = await req.json()
        username = body.get('username')
        
        if not username:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Username is required'
                })
            }
        
        # Run the search
        result = await search_username(username)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

serve(handle_request) 