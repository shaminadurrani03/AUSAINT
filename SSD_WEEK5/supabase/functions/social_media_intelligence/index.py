import os
import json
from typing import Dict, Any, List
import httpx
import re
import asyncio
from supabase.functions import serve

# Security measures
API_KEY = os.environ.get("SOCIAL_OSINT_API_KEY")
MAX_REQUESTS_PER_MINUTE = 5  # Rate limiting
ALLOWED_DOMAINS = ["localhost:3000", "ausaint.com"]  # CORS protection

# Sherlock Path
SHERLOCK_PATH = "/Users/BILAL/Desktop/Github/AUSAINT/SSD_WEEK5/backend/api/sherlock"  # <-- Replace this with actual path

async def search_username(username: str) -> Dict[str, Any]:
    """Search for a username across multiple social platforms using Sherlock"""
    if not os.path.exists(SHERLOCK_PATH):
        return {"error": "Sherlock not found on server."}

    try:
        process = await asyncio.create_subprocess_exec(
            "python3", SHERLOCK_PATH, username, "--print-found",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            return {"error": stderr.decode()}

        output_lines = stdout.decode().splitlines()
        found_platforms = [{"url": line, "exists": True} for line in output_lines if line.startswith("http")]

        return {
            "username": username,
            "platforms_found": len(found_platforms),
            "platforms": found_platforms
        }

    except Exception as e:
        return {"error": str(e)}


async def analyze_social_profile(platform: str, username: str) -> Dict[str, Any]:
    """Get detailed information about a specific social media profile using Twint"""
    try:
        import twint
        import nest_asyncio
        nest_asyncio.apply()

        c = twint.Config()
        c.Username = username
        c.Store_object = True
        c.Hide_output = True

        twint.run.Lookup(c)
        user_info = twint.output.users_list[0] if twint.output.users_list else None

        if not user_info:
            return {"error": "No profile found."}

        return {
            "platform": platform,
            "username": user_info.username,
            "profile_info": {
                "fullName": user_info.name,
                "bio": user_info.bio,
                "location": user_info.location,
                "joinDate": user_info.join_date,
                "followers": user_info.followers,
                "following": user_info.following
            },
            "recent_activity": []  # Optional: Extend this with Tweets later
        }

    except Exception as e:
        return {"error": str(e)}


async def handle_request(req):
    # Check request origin for CORS
    origin = req.headers.get("origin", "")
    if not any(allowed in origin for allowed in ALLOWED_DOMAINS):
        return {"statusCode": 403, "body": json.dumps({"error": "Forbidden"})}

    # Get the current user ID from Supabase Auth
    user_id = req.headers.get("x-supabase-auth-user-id")
    if not user_id:
        return {"statusCode": 401, "body": json.dumps({"error": "Unauthorized"})}

    # Parse request body
    try:
        body = await req.json()
        action = body.get("action")
        username = body.get("username")
        platform = body.get("platform")

        if not action or not username:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing required parameters"})}

        if not re.match(r"^[a-zA-Z0-9._-]+$", username):
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid username format"})}

        if action == "search":
            result = await search_username(username)
        elif action == "analyze" and platform:
            result = await analyze_social_profile(platform, username)
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid action or missing platform"})}

        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "data": result,
                "user_id": user_id
            })
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


serve(handle_request)
