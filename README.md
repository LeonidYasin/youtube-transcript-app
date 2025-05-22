# YouTube Transcript API

A FastAPI-based web service for extracting and processing YouTube video transcripts with support for multiple languages.

## Table of Contents
- [Features](#features)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Rate Limiting](#rate-limiting)
  - [Endpoints](#endpoints)
    - [Get Transcript](#get-transcript)
    - [List Available Languages](#list-available-languages)
    - [Get Channel Videos](#get-channel-videos)
    - [Search Channels](#search-channels)
    - [Get Rabbi Ginsburgh's Channel](#get-rabbi-ginsburghs-channel)
  - [Error Handling](#error-handling)
  - [Response Format](#response-format)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Development](#development)
- [License](#license)

## Features

- Extract transcripts from YouTube videos by URL or video ID
- Support for multiple languages
- Clean and format transcript text
- Simple RESTful API
- Interactive API documentation with Swagger UI
- Built-in logging
- CORS support
- Health check endpoint
- Channel video listing
- Channel search functionality

## API Documentation

### Authentication
Currently, the API does not require authentication. However, it's recommended to implement API key authentication for production use.

### Rate Limiting
- Default rate limit: 100 requests per minute per IP address
- Headers:
  - `X-RateLimit-Limit`: Maximum number of requests allowed
  - `X-RateLimit-Remaining`: Remaining number of requests
  - `X-RateLimit-Reset`: Time when the rate limit resets (UTC timestamp)

### Endpoints

#### Get Transcript

```http
GET /api/transcript/api/transcript?url={video_url}&language={language_code}
```

**Parameters:**
- `url` (required): YouTube video URL or video ID
- `language` (optional, default: 'en'): Language code for the transcript

**Example Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/transcript/api/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&language=ru' \
  -H 'accept: application/json'
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "video_id": "dQw4w9WgXcQ",
  "language": "ru",
  "segments": [
    {
      "start": "0:00:00.440",
      "end": "0:00:03.710",
      "text": "Привет, как дела?"
    },
    {
      "start": "0:00:03.710",
      "end": "0:00:05.500",
      "text": "Спасибо, отлично!"
    }
  ]
}
```

#### List Available Languages

```http
GET /api/languages/api/available-languages
```

**Example Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/languages/api/available-languages' \
  -H 'accept: application/json'
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "languages": [
    {"code": "en", "name": "English"},
    {"code": "ru", "name": "Russian"},
    {"code": "he", "name": "Hebrew"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"}
  ]
}
```

#### Get Channel Videos

```http
GET /api/channel-search/{channel_id}/videos?max_results={max_results}
```

**Parameters:**
- `channel_id` (required): YouTube channel ID
- `max_results` (optional, default: 10, max: 50): Number of videos to return

**Example Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/channel-search/UCKadAPtEb8TTfPrQY3qwKpQ/videos?max_results=5' \
  -H 'accept: application/json'
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "channel_id": "UCKadAPtEb8TTfPrQY3qwKpQ",
  "videos": [
    {
      "video_id": "xXU4-tiX4Wk",
      "title": "הרב יצחק גינזבורג - איך למצוא את השליחות שלי",
      "url": "https://www.youtube.com/watch?v=xXU4-tiX4Wk",
      "duration": "25:21",
      "view_count": "319 views",
      "published_time": "13 days ago",
      "thumbnail": "https://img.youtube.com/vi/xXU4-tiX4Wk/hqdefault.jpg"
    }
  ],
  "count": 1
}
```

#### Search Channels

```http
GET /api/channel-search/search?query={search_query}&max_results={max_results}
```

**Parameters:**
- `query` (required): Search query
- `max_results` (optional, default: 5, max: 20): Number of results to return

**Example Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/channel-search/search?query=Rabbi%20Ginsburgh&max_results=3' \
  -H 'accept: application/json'
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "query": "Rabbi Ginsburgh",
  "results": [
    {
      "channel_id": "UCKadAPtEb8TTfPrQY3qwKpQ",
      "title": "הרב יצחק גינזבורג - הרצאות ושיעורים | Rabbi Yitzchak Ginsburgh",
      "description": "הרצאות ושיעורים מהרב יצחק גינזבורג שליט"א",
      "thumbnail": "https://yt3.googleusercontent.com/...",
      "subscriber_count": "125K"
    }
  ],
  "count": 1
}
```

#### Get Rabbi Ginsburgh's Channel

```http
GET /api/channel-search/rabbi-ginsburgh
```

**Example Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/channel-search/rabbi-ginsburgh' \
  -H 'accept: application/json'
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "channel": {
    "channel_id": "UCKadAPtEb8TTfPrQY3qwKpQ",
    "title": "הרב יצחק גינזבורג - הרצאות ושיעורים | Rabbi Yitzchak Ginsburgh",
    "description": "הרצאות ושיעורים מהרב יצחק גינזבורג שליט"א",
    "url": "https://www.youtube.com/channel/UCKadAPtEb8TTfPrQY3qwKpQ",
    "subscriber_count": "125K",
    "video_count": "1,234"
  }
}
```

### Error Handling

#### Response Format
All error responses follow this format:
```json
{
  "status": "error",
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      "field_name": "Additional error details"
    }
  }
}
```

#### Common Error Codes

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | BAD_REQUEST | Invalid request parameters |
| 404 | NOT_FOUND | The requested resource was not found |
| 422 | VALIDATION_ERROR | Request validation failed |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_SERVER_ERROR | Internal server error |
| 503 | SERVICE_UNAVAILABLE | Service temporarily unavailable |

**Example Error Response (404 Not Found):**
```json
{
  "status": "error",
  "error": {
    "code": "NOT_FOUND",
    "message": "Video not found or has no captions available",
    "details": {
      "video_id": "nonexistent_video_id"
    }
  }
}
```

**Example Error Response (429 Too Many Requests):**
```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again in 60 seconds.",
    "details": {
      "retry_after": 60
    }
  }
}
```

### Response Format

All successful responses include a `status` field indicating the result of the operation:

```json
{
  "status": "success",
  // Additional data fields...
}
```

For paginated responses:
```json
{
  "status": "success",
  "data": [
    // Array of items
  ],
  "pagination": {
    "total": 100,
    "count": 10,
    "per_page": 10,
    "current_page": 1,
    "total_pages": 10
  }
}
```

## Interactive Documentation

For interactive documentation and to try out the API endpoints, visit:
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`

Both interfaces are automatically generated from the OpenAPI specification available at `/api/openapi.json`.

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- yt-dlp (installed automatically)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd youtube-transcript-api
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root to customize the application settings:

```env
HOST=0.0.0.0
PORT=8000
LOG_FILE=logs/youtube_transcript.log
```

## Usage

### Running the Server

```bash
# Run with auto-reload (development)
python run.py

# Or directly with uvicorn
uvicorn app.main:app --reload
```

### API Endpoints

- `GET /` - Web interface for testing the API
- `GET /api/transcript` - Get transcript for a YouTube video
  - Parameters:
    - `url`: YouTube video URL or ID (required)
    - `language`: Language code (default: 'ru')
- `GET /api/available-languages` - Get list of supported languages
- `GET /health` - Health check endpoint
- `GET /api/docs` - Interactive API documentation (Swagger UI)
- `GET /api/redoc` - Alternative API documentation (ReDoc)

### Example Requests

```bash
# Get transcript for a video
curl "http://localhost:8000/api/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&language=en"

# Get available languages
curl "http://localhost:8000/api/available-languages"
```

## Project Structure

```
youtube_transcript_app/
├── app/                      # Main application package
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application setup
│   ├── config.py             # Configuration settings
│   ├── routes/               # API routes
│   │   ├── __init__.py
│   │   ├── transcript.py     # Transcript endpoints
│   │   └── languages.py      # Language endpoints
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── youtube.py        # YouTube API integration
│   │   └── subtitles.py      # Subtitle processing
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   └── helpers.py        # Helper functions
│   └── models/               # Data models
│       ├── __init__.py
│       └── schemas.py        # Pydantic schemas
├── tests/                    # Test files
├── .env.example              # Example environment variables
├── requirements.txt          # Project dependencies
└── run.py                   # Application entry point
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)

## Запуск

1. Перейдите в папку с приложением:
   ```
   cd путь_к_папке\youtube_transcript_app
   ```
2. Запустите сервер:
   ```
   python fastapi_server.py
   ```
3. Откройте браузер и перейдите по адресу:
   ```
   http://localhost:8000
   ```

## Использование

1. Введите URL видео с YouTube в поле ввода
2. Нажмите кнопку "Получить транскрипт"
3. Транскрипт появится в поле ниже

## Примечания

- Приложение использует неофициальный API YouTube, который может блокировать запросы при частом использовании
- Логи приложения сохраняются в файл `youtube_fastapi.log`
- Для работы приложения требуется подключение к интернету
