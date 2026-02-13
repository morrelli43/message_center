#!/usr/bin/env python3
"""
Example client for sending messages to the Message Center.

Usage:
    python example_client.py "Your message here"
    python example_client.py "Warning message" --priority warning
    python example_client.py "Error occurred" --priority error --source "MyApp"
"""

import argparse
import requests
import json
import sys


def send_message(message, source="ExampleClient", priority="info", metadata=None, host="localhost", port=5000):
    """
    Send a message to the Message Center.
    
    Args:
        message: The message content
        source: The source application name
        priority: Priority level (info, warning, error)
        metadata: Optional metadata dictionary
        host: Message Center host
        port: Message Center port
        
    Returns:
        Response from the server
    """
    url = f"http://{host}:{port}/api/message"
    
    payload = {
        "source": source,
        "message": message,
        "priority": priority,
        "metadata": metadata or {}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Send a message to the Message Center",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python example_client.py "Hello, World!"
  python example_client.py "Backup completed" --source "BackupScript"
  python example_client.py "Disk space low" --priority warning
  python example_client.py "Database connection failed" --priority error
        """
    )
    
    parser.add_argument("message", help="The message to send")
    parser.add_argument("--source", default="ExampleClient", help="Source application name")
    parser.add_argument("--priority", choices=["info", "warning", "error"], 
                       default="info", help="Message priority")
    parser.add_argument("--host", default="localhost", help="Message Center host")
    parser.add_argument("--port", type=int, default=5000, help="Message Center port")
    parser.add_argument("--metadata", help="JSON metadata to include")
    
    args = parser.parse_args()
    
    # Parse metadata if provided
    metadata = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON metadata: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Send the message
    result = send_message(
        message=args.message,
        source=args.source,
        priority=args.priority,
        metadata=metadata,
        host=args.host,
        port=args.port
    )
    
    print(f"✓ Message sent successfully!")
    print(f"  Status: {result.get('status')}")


if __name__ == "__main__":
    main()
