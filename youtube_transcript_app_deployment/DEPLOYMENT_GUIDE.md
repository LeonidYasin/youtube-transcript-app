# YouTube Transcript API - Deployment Guide

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Installation

1. Clone or extract the deployment package to your server
2. Navigate to the deployment directory:
   ```
   cd youtube_transcript_app_deployment
   ```
3. Create a Python virtual environment (recommended):
   ```
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
   Or use the frozen requirements for exact versions:
   ```
   pip install -r requirements_frozen.txt
   ```

## Configuration

1. Rename `.env.example` to `.env` and update the configuration as needed:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file with your preferred text editor.

## Running the Application

1. Start the FastAPI server:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   - `--host 0.0.0.0` makes the server accessible from other machines
   - `--port 8000` specifies the port (default is 8000)

2. For production use, consider using a process manager like:
   - Gunicorn with Uvicorn workers
   - Supervisor
   - Systemd service

## API Endpoints

- `GET /api/transcript/?url=YOUTUBE_URL&language=ru` - Get transcript for a YouTube video
  - `url`: YouTube video URL or ID (required)
  - `language`: Language code (e.g., 'en', 'ru', 'es')
  - `auto_generated`: true/false (whether to use auto-generated subtitles)

## Logs

Application logs are stored in the `logs/` directory.

## Updating

To update the application:
1. Stop the running server
2. Replace the files with the new version
3. Install any new dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Restart the server

## Troubleshooting

- If you see import errors, make sure all dependencies are installed
- Check the logs in the `logs/` directory for error messages
- Make sure the port (default 8000) is not blocked by a firewall
