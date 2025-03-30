from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from os import environ

# Initialize FastMCP server
mcp = FastMCP("lastfm")

LASTFM_API_KEY = environ.get("LASTFM_API_KEY")

# Constants
LASTFM_BASE = "http://ws.audioscrobbler.com/2.0/"

USER_AGENT = "lastfm_app/1.0"

async def make_lastfm_request(url: str) -> dict[str, Any] | None:
    """Make a request to the lastfm with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def get_lastfm_top_tracks(limit: int=50) -> str:
    """
    Get current global top tracks on last.fm
    """
    general_top_tracks = f"{LASTFM_BASE}?method=chart.gettoptracks" \
                f"&api_key={LASTFM_API_KEY}&format=json&limit={limit}" 

    top_tracks = await make_lastfm_request(general_top_tracks)

    if not top_tracks:
        return "Unable to fetch top track data."

    top_tracks = top_tracks['tracks']['track']

    if not isinstance(top_tracks, list):
        return "API output not as expected - not a list"
    
    tracks_output = []
    for track in top_tracks:
        track_info = f"{track['name']} by {track['artist']['name']}"
        
        tracks_output.append(track_info)
    return "\n---\n".join(tracks_output)

@mcp.tool()
async def get_users_weeks_top_tracks(user_name: str) -> str:
    """Get top weekly track data for a user from Last.fm.

    Args:
        user_name: user name of Last.fm user
    """
    # First get the forecast grid endpoint
    weekly_track_url = f"{LASTFM_BASE}?method=user.getweeklytrackchart&user={user_name}" \
                        f"&format=json&api_key={LASTFM_API_KEY}"

    top_week_track_data = await make_lastfm_request(weekly_track_url)

    if not top_week_track_data:
        return "Unable to fetch top weekly track data."

    # Format the periods into a readable forecast
    tracks = top_week_track_data['weeklytrackchart']['track']
    if not isinstance(tracks, list):
        return "API output not as expected"
    tracks_output = []
    for track in tracks[:10]:  # Only show next 5 periods
        track_info = f"{track['@attr']['rank']}: {track['name']} by " \
                        f"{track['artist']['#text']} " \
                        f"({track['playcount']} plays)"
        
        tracks_output.append(track_info)
    return "\n---\n".join(tracks_output)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')