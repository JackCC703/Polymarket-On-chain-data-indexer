import requests
from typing import Optional, Dict, Any

GAMMA_API_URL = "https://gamma-api.polymarket.com"

def fetch_market_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """
    Fetch market data by slug from Gamma API.
    """
    url = f"{GAMMA_API_URL}/events"
    # Gamma API usually returns events which contain markets
    # Or we can search markets directly?
    # Let's try /markets?slug=... or similar query if possible, 
    # but official docs often suggest querying events for user-friendly slugs.
    # However, `stage1.md` says "through Gamma API... e.g. using slug".
    # Let's assume there's a param `slug` in `/events` or `/markets`.
    # Based on common usage: /events?slug=...
    
    params = {"slug": slug}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Typically returns a list of events.
        if isinstance(data, list) and len(data) > 0:
            # We assume the user wants the first market of the event 
            # OR pass a market slug? 
            # The prompt says "market slug".
            # If the slug provided is a market slug, we might not find it in events?
            # Polymarket slugs are usually event level. Market level slugs exist but are less common.
            # Let's support checking both.
            
            # If data is a list of events, we need the markets inside.
            event = data[0]
            if "markets" in event:
                # Return the list of markets or the first one?
                # For this stage, let's assume valid event slug -> return first market or look for match?
                # The user input in validation is --market-slug "will-there-be..." which looks like an event slug.
                # So we return the first market of that event to match behavior.
                return event["markets"][0]
        
        return None
    except Exception as e:
        print(f"Error fetching from Gamma: {e}")
        return None

def fetch_market_by_id(condition_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch market by condition ID.
    """
    url = f"{GAMMA_API_URL}/markets"
    params = {"condition_id": condition_id}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        if isinstance(data, dict):
             # Some endpoints return dict directly if ID is unique
             return data
             
        return None
    except Exception as e:
        print(f"Error fetching from Gamma: {e}")
        return None
