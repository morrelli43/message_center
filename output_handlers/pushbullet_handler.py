"""
Pushbullet output handler for Message Center.
Sends messages to Pushbullet devices.
"""

import requests


def create_pushbullet_handler(api_key):
    """
    Create a Pushbullet output handler with the given API key.
    
    Args:
        api_key: Pushbullet API key
        
    Returns:
        Handler function that sends messages to Pushbullet
    """
    
    def pushbullet_handler(message_data):
        """Send message to Pushbullet."""
        url = "https://api.pushbullet.com/v2/pushes"
        headers = {
            "Access-Token": api_key,
            "Content-Type": "application/json"
        }
        
        # Prepare notification data
        title = f"{message_data.get('source', 'Message Center')}"
        body = message_data.get('message', 'No message content')
        priority = message_data.get('priority', 'info')
        
        # Add priority indicator to title
        if priority == 'error':
            title = f"🚨 {title}"
        elif priority == 'warning':
            title = f"⚠️ {title}"
        else:
            title = f"📬 {title}"
        
        payload = {
            "type": "note",
            "title": title,
            "body": body
        }
        
        # Send to Pushbullet
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    return pushbullet_handler
