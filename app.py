"""
Message Center - Centralized Message Relay Service
A service that receives messages from local programs and relays them to various outputs.
"""

import os
import json
from datetime import datetime
from collections import deque
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory message storage
MAX_MESSAGES = int(os.environ.get('MAX_MESSAGES', 100))
messages = deque(maxlen=MAX_MESSAGES)

# Output handlers registry
output_handlers = {}


def register_output_handler(name, handler):
    """Register an output handler function."""
    output_handlers[name] = handler


def broadcast_message(message_data):
    """Send message to all registered output handlers."""
    for handler_name, handler in output_handlers.items():
        try:
            handler(message_data)
        except Exception as e:
            app.logger.error(f"Error in output handler '{handler_name}': {e}")


# Default console output handler
def console_output_handler(message_data):
    """Print message to console/log."""
    timestamp = message_data.get('timestamp', 'N/A')
    source = message_data.get('source', 'Unknown')
    content = message_data.get('message', '')
    print(f"[{timestamp}] [{source}] {content}")


# Register default handler
register_output_handler('console', console_output_handler)


@app.route('/')
def index():
    """Serve the HTML dashboard."""
    return render_template('index.html')


@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all stored messages."""
    return jsonify({'messages': list(messages)})


@app.route('/api/message', methods=['POST'])
def receive_message():
    """
    Receive a message via HTTP POST.
    Expected JSON format:
    {
        "source": "application_name",
        "message": "message content",
        "priority": "info|warning|error",
        "metadata": {}  // optional additional data
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        if 'message' not in data:
            return jsonify({'error': 'Missing required field: message'}), 400
        
        # Add timestamp if not provided
        if 'timestamp' not in data:
            from datetime import timezone
            data['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Set defaults
        data.setdefault('source', 'Unknown')
        data.setdefault('priority', 'info')
        data.setdefault('metadata', {})
        
        # Store message
        messages.append(data)
        
        # Broadcast to output handlers
        broadcast_message(data)
        
        # Emit to WebSocket clients
        socketio.emit('new_message', data)
        
        return jsonify({'status': 'success', 'message': 'Message received'}), 200
        
    except Exception as e:
        app.logger.error(f"Error processing message: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message_count': len(messages),
        'output_handlers': list(output_handlers.keys())
    })


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    emit('connection_status', {'status': 'connected'})


@socketio.on('request_messages')
def handle_request_messages():
    """Send all messages to newly connected client."""
    emit('all_messages', {'messages': list(messages)})


def load_pushbullet_handler():
    """Load Pushbullet output handler if API key is configured."""
    api_key = os.environ.get('PUSHBULLET_API_KEY')
    
    if api_key and api_key != 'your_api_key_here':
        try:
            from output_handlers.pushbullet_handler import create_pushbullet_handler
            handler = create_pushbullet_handler(api_key)
            register_output_handler('pushbullet', handler)
            app.logger.info("Pushbullet output handler loaded")
        except ImportError:
            app.logger.warning("Pushbullet handler not available")
        except Exception as e:
            app.logger.error(f"Error loading Pushbullet handler: {e}")


if __name__ == '__main__':
    # Load additional output handlers
    load_pushbullet_handler()
    
    # Start server
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting Message Center on {host}:{port}")
    print(f"Registered output handlers: {list(output_handlers.keys())}")
    
    # Use debug mode only in development
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Note: allow_unsafe_werkzeug is needed for development server
    # In production, use a proper WSGI server like Gunicorn
    socketio.run(app, host=host, port=port, debug=debug_mode, allow_unsafe_werkzeug=True)
