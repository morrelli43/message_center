# Message Center 📬

A centralized message hub that receives message strings from locally running programs or scripts and relays them to any output method you want (e.g., Pushbullet for smartwatch notifications).

## Features

- **REST API** for receiving JSON-formatted messages
- **Real-time HTML dashboard** with WebSocket updates
- **Plugin architecture** for output methods (Pushbullet, console, etc.)
- **Dockerized** for easy deployment
- **In-memory message storage** with configurable retention
- **Priority levels** (info, warning, error)
- **Custom metadata** support

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/morrelli43/message_center.git
cd message_center
```

2. Start the service:
```bash
docker-compose up -d
```

3. Access the dashboard at `http://localhost:5000`

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

3. Access the dashboard at `http://localhost:5000`

## Sending Messages

### Using the Example Client

```bash
# Simple message
python example_client.py "Hello, World!"

# With priority and source
python example_client.py "Backup completed" --source "BackupScript" --priority info

# Warning message
python example_client.py "Disk space low" --priority warning

# Error message
python example_client.py "Database connection failed" --priority error --source "MyApp"
```

### Using cURL

```bash
curl -X POST http://localhost:5000/api/message \
  -H "Content-Type: application/json" \
  -d '{
    "source": "MyScript",
    "message": "Task completed successfully",
    "priority": "info",
    "metadata": {"task_id": "123", "duration": "5s"}
  }'
```

### Message Format

Messages must be JSON with the following structure:

```json
{
  "source": "ApplicationName",      // Required: Source of the message
  "message": "Message content",     // Required: The message text
  "priority": "info",               // Optional: info|warning|error (default: info)
  "metadata": {}                    // Optional: Additional data
}
```

## Configuration

Configuration is done via environment variables or a `.env` file:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=5000

# Message retention (number of messages to keep in memory)
MAX_MESSAGES=100

# Pushbullet Configuration (optional)
PUSHBULLET_API_KEY=your_api_key_here
```

Copy `.env.example` to `.env` and adjust the values:
```bash
cp .env.example .env
```

## Output Handlers

### Console Output
Always enabled. Messages are printed to the console/logs.

### Pushbullet
To enable Pushbullet notifications:

1. Get your API key from https://www.pushbullet.com/#settings/account
2. Set the `PUSHBULLET_API_KEY` environment variable
3. Restart the service

Messages will be sent to all your Pushbullet devices (including smartwatches).

### Adding Custom Output Handlers

Create a new handler in `output_handlers/`:

```python
# output_handlers/my_handler.py
def create_my_handler(config):
    def my_handler(message_data):
        # Process message_data
        source = message_data.get('source')
        message = message_data.get('message')
        priority = message_data.get('priority')
        # Send to your service
        pass
    return my_handler
```

Register it in `app.py`:

```python
from output_handlers.my_handler import create_my_handler
handler = create_my_handler(config)
register_output_handler('my_handler', handler)
```

## API Endpoints

### POST /api/message
Receive a new message.

**Request:**
```json
{
  "source": "MyApp",
  "message": "Hello",
  "priority": "info",
  "metadata": {}
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Message received"
}
```

### GET /api/messages
Get all stored messages.

**Response:**
```json
{
  "messages": [...]
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message_count": 42,
  "output_handlers": ["console", "pushbullet"]
}
```

## Docker Deployment

### Building the Image

```bash
docker build -t message-center .
```

### Running with Docker Compose

```bash
docker-compose up -d
```

### Environment Variables in Docker

Edit `docker-compose.yml` to set environment variables:

```yaml
environment:
  - PUSHBULLET_API_KEY=your_key_here
  - MAX_MESSAGES=200
```

Or use a `.env` file and uncomment the volume mount in `docker-compose.yml`.

## Use Cases

- **Website notifications**: Get notifications when someone submits a form
- **Script monitoring**: Monitor long-running scripts and get alerts
- **System monitoring**: Receive alerts for system events
- **Build notifications**: Get notified when CI/CD builds complete
- **Error tracking**: Get immediate alerts for application errors
- **IoT devices**: Receive notifications from IoT devices

## Development

### Project Structure

```
message_center/
├── app.py                      # Main Flask application
├── templates/
│   └── index.html             # Dashboard HTML
├── output_handlers/
│   ├── __init__.py
│   └── pushbullet_handler.py  # Pushbullet integration
├── example_client.py          # Example client script
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker Compose configuration
└── .env.example              # Example environment variables
```

## License

MIT

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.
