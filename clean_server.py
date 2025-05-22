from fastapi import FastAPI, Request, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re
import logging
import os
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("youtube_transcript.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Transcript API",
    description="API для получения транскриптов YouTube видео",
    version="1.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели ответов
class TranscriptResponse(BaseModel):
    success: bool
    video_id: str
    transcript: Optional[str] = None
    error: Optional[str] = None
    language: Optional[str] = None
    is_generated: Optional[bool] = None

# Вспомогательные функции
def extract_video_id(url: str) -> Optional[str]:
    """Извлекает ID видео из URL YouTube."""
    patterns = [
        r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# API Endpoints
@app.get("/api/transcript", response_model=TranscriptResponse)
async def get_transcript(
    response: Response,
    url: str = Query(..., description="YouTube video URL"),
    language: str = Query('ru', description="Preferred language code (e.g., 'ru', 'en'), or 'any' for first available")
):
    """Получить транскрипт для указанного видео YouTube."""
    logger.info(f"Получен запрос на получение транскрипта для видео: {url}")
    
    try:
        # Извлекаем ID видео из URL
        video_id = extract_video_id(url)
        if not video_id:
            error_msg = "Не удалось извлечь ID видео из URL"
            logger.error(f"{error_msg}: {url}")
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"success": False, "error": error_msg, "video_id": ""}
        
        logger.info(f"Извлечен ID видео: {video_id}")
        
        try:
            # Пробуем получить список доступных транскриптов
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Пробуем найти запрошенный язык
            try:
                if language.lower() == 'any':
                    # Берем первый доступный транскрипт
                    transcript = transcript_list.find_transcript(['ru', 'en'])
                else:
                    # Пробуем найти точное совпадение по языку
                    transcript = transcript_list.find_transcript([language])
                
                # Получаем транскрипт
                transcript_data = transcript.fetch()
                transcript_text = "\n".join([t['text'] for t in transcript_data])
                
                return {
                    "success": True,
                    "video_id": video_id,
                    "transcript": transcript_text,
                    "language": transcript.language_code,
                    "is_generated": transcript.is_generated
                }
                
            except Exception as e:
                logger.warning(f"Не удалось найти транскрипт на языке {language}: {str(e)}")
                
                # Пробуем найти русский как запасной вариант
                if language != 'ru':
                    try:
                        transcript = transcript_list.find_transcript(['ru'])
                        transcript_data = transcript.fetch()
                        transcript_text = "\n".join([t['text'] for t in transcript_data])
                        
                        return {
                            "success": True,
                            "video_id": video_id,
                            "transcript": transcript_text,
                            "language": transcript.language_code,
                            "is_generated": transcript.is_generated,
                            "note": f"Транскрипт на запрошенном языке ({language}) не найден, возвращен русский перевод"
                        }
                    except Exception as e2:
                        logger.warning(f"Не удалось найти русский транскрипт: {str(e2)}")
                
                # Если ничего не нашли, возвращаем ошибку
                response.status_code = status.HTTP_404_NOT_FOUND
                return {
                    "success": False,
                    "video_id": video_id,
                    "error": f"Не удалось найти транскрипт на запрошенном языке: {language}"
                }
                
        except Exception as e:
            logger.error(f"Ошибка при получении транскрипта: {str(e)}", exc_info=True)
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {
                "success": False,
                "video_id": video_id,
                "error": f"Ошибка при получении транскрипта: {str(e)}"
            }
    
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {str(e)}", exc_info=True)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "success": False,
            "video_id": "",
            "error": f"Внутренняя ошибка сервера: {str(e)}"
        }

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("clean_server:app", host="0.0.0.0", port=8080, reload=True)
