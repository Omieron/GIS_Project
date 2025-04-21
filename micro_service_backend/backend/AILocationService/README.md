# Smart Location AI Service

A FastAPI-based service that processes natural language location queries using OpenAI's GPT models and provides location-based services with support for Foursquare API integration.

## Features

- **User Location Detection**: Determines the user's current location based on IP address
- **Defined Location Search**: Finds coordinates for specific named locations
- **Contextual Location Search**: Locates places near other locations (e.g., "coffee shops near university")
- **GPT-powered Natural Language Processing**: Intelligently interprets location queries
- **Conversation-based Context**: Maintains conversation history for contextual queries
- **Foursquare API Integration**: High-quality place search results with detailed information
- **Food & Restaurant Search**: Find places to eat specific dishes (e.g., "iskender in Bursa")
- **Turkish Language Support**: Full support for Turkish language queries

## Requirements

- Python 3.9+
- FastAPI
- Uvicorn
- OpenAI Python SDK
- GeoPy
- python-dotenv
- Requests
- Foursquare API SDK

## Installation

1. Clone the repository:

```bash
git clone [your-repository-url]
cd AILocationService
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key
FOURSQUARE_API_KEY=your_foursquare_api_key
```

You can obtain a Foursquare API key by signing up at [Foursquare Developer Portal](https://developer.foursquare.com/).

## Running the Application

Start the application using Uvicorn:

```bash
uvicorn main:app --reload
```

The application will be available at http://127.0.0.1:8000

## API Endpoints

### Root Endpoint

- `GET /`: Redirects to the Swagger documentation
- `GET /health`: Check if the backend is running

### Location Endpoint

- `POST /location/`: Process location queries
  - Required Parameter: `prompt` (string) - Natural language query about location
  - Optional Parameter: `conversation_id` (string) - ID to maintain conversation context

## Usage Examples

### Check if Backend is Running

```
GET /health
```

Response:
```json
{
  "status": "backend running"
}
```

### Process a Location Query

```
POST /location/
```

With the following parameter:
- `prompt`: "Where am I?"

Response (example):
```json
{
  "type": "user-location",
  "location": {
    "ip": "123.45.67.89",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "city": "New York",
    "country": "United States"
  }
}
```

Other query examples:
- "Where is Bilkent University?"
- "Find a coffee shop near Central Park"
- "Bilkent Üniversitesinde bir kahveci" (Turkish: A coffee shop at Bilkent University)
- "Bursa'da iskender yemek istiyorum" (Turkish: I want to eat iskender in Bursa)
- "daha merkeze yakın" (Turkish: closer to the center) - works within a conversation

## Project Structure

- `main.py`: Application entry point and root endpoint
- `routers/location.py`: Location router with main processing endpoint
- `services/`: 
  - `gpt.py`: Handles OpenAI GPT integration for query interpretation
  - `geocode.py`: Manages geocoding services
  - `places.py`: Handles OpenStreetMap place search functionality
  - `foursquare.py`: Foursquare API integration for better place search
  - `user_location.py`: Manages user location detection
  - `conversations.py`: Handles conversation history and context
  - `food.py`: Specialized service for finding restaurants serving specific dishes

## License

[Your license information]

## Contributing

[Your contribution guidelines]
