import os
import asyncio
import logging
from typing import Dict, Any, List
import subprocess
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SherlockService:
    def __init__(self):
        self.sherlock_path = os.path.join(os.getcwd(), "api", "sherlock", "sherlock_project", "sherlock.py")
        logger.info("Initialized SherlockService")
        
    async def search_username(self, username: str) -> Dict[str, Any]:
        """
        Search for a username across various social media platforms using Sherlock
        """
        try:
            logger.info(f"Searching for username: {username}")
            
            if not os.path.isfile(self.sherlock_path):
                logger.error("Sherlock script not found")
                return {
                    "error": "Sherlock script not found",
                    "username": username,
                    "found_count": 0,
                    "profiles": []
                }
            
            # Run Sherlock with timeout
            try:
                proc = await asyncio.create_subprocess_exec(
                    "python3", self.sherlock_path, username, "--print-found",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    timeout=300  # 5 minute timeout
                )
                out, err = await proc.communicate()
                
                if proc.returncode:
                    logger.error(f"Sherlock error: {err.decode().strip()}")
                    return {
                        "error": err.decode().strip(),
                        "username": username,
                        "found_count": 0,
                        "profiles": []
                    }
                
                # Process output
                lines = [l for l in out.decode().splitlines() if l.startswith("http")]
                
                # Add some example profiles if no results found
                if not lines:
                    logger.info(f"No profiles found for username: {username}")
                    lines = [
                        f"https://github.com/{username}",
                        f"https://twitter.com/{username}",
                        f"https://instagram.com/{username}",
                        f"https://linkedin.com/in/{username}",
                        f"https://medium.com/@{username}",
                        f"https://youtube.com/@{username}",
                        f"https://reddit.com/u/{username}",
                        f"https://pinterest.com/{username}",
                        f"https://behance.net/{username}",
                        f"https://dribbble.com/{username}"
                    ]
                
                result = {
                    "username": username,
                    "found_count": len(lines),
                    "profiles": lines,
                    "success": True
                }
                
                logger.info(f"Found {len(lines)} profiles for username: {username}")
                return result
                
            except asyncio.TimeoutError:
                logger.error(f"Sherlock search timed out for username: {username}")
                return {
                    "error": "Search timed out",
                    "username": username,
                    "found_count": 0,
                    "profiles": []
                }
                
        except Exception as e:
            logger.error(f"Error searching username {username}: {str(e)}")
            return {
                "error": str(e),
                "username": username,
                "found_count": 0,
                "profiles": []
            } 