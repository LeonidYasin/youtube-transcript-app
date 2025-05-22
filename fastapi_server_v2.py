from fastapi import FastAPI, Request, Response, Query, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import json

# Импортируем наш сервис транскрипции
from transcript_service import get_transcript, extract_video_id, get_available_languages, detect_language

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# Создаем экземпляр FastAPI
app = FastAPI(
    title="YouTube Transcript API",
    description="API для получения транскриптов YouTube видео на любом доступном языке",
    version="2.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple HTML form for testing
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Transcript API</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { margin-top: 20px; }
        input[type="text"] { width: 70%; padding: 10px; margin-right: 10px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        #result { margin-top: 20px; white-space: pre-wrap; border: 1px solid #ddd; padding: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>YouTube Transcript API</h1>
        <p>Введите URL YouTube видео, чтобы получить его транскрипт:</p>
        <div>
            <input type="text" id="videoUrl" placeholder="https://www.youtube.com/watch?v=...">
            <button onclick="getTranscript()">Получить транскрипт</button>
        </div>
        <div>
            <label for="language">Язык (оставьте пустым для любого):</label>
            <input type="text" id="language" placeholder="ru, en, es, etc.">
        </div>
        <div id="result"></div>
    </div>
    <script>
        async function getTranscript() {
            const url = document.getElementById('videoUrl').value;
            const language = document.getElementById('language').value || 'any';
            const resultDiv = document.getElementById('result');
            
            if (!url) {
                resultDiv.textContent = 'Пожалуйста, введите URL видео';
                return;
            }
            
            resultDiv.textContent = 'Загрузка...';
            
            try {
                const response = await fetch(`/api/transcript?url=${encodeURIComponent(url)}&language=${language}`);
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <h3>Транскрипт (${data.language}):</h3>
                        <p>${data.transcript.replace(/\n/g, '<br>')}</p>
                        <p><strong>Доступные языки:</strong> ${data.available_languages?.join(', ') || 'Неизвестно'}</p>
                    `;
                } else {
                    resultDiv.textContent = `Ошибка: ${data.error}`;
                    if (data.available_languages?.length > 0) {
                        resultDiv.textContent += `\nДоступные языки: ${data.available_languages.join(', ')}`;
                    }
                }
            } catch (error) {
                resultDiv.textContent = `Произошла ошибка: ${error.message}`;
            }
        }
    </script>
</body>
</html>
"""

class TranscriptRequest(BaseModel):
    url: str
    language: Optional[str] = "any"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница с формой для ввода URL"""
    return HTMLResponse(content=HTML_FORM, status_code=200)
                #result { margin-top: 20px; white-space: pre-wrap; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>YouTube Transcript API</h1>
                <p>Введите URL YouTube видео, чтобы получить его транскрипт:</p>
                <div>
                    <input type="text" id="videoUrl" placeholder="https://www.youtube.com/watch?v=...">
                    <button onclick="getTranscript()">Получить транскрипт</button>
                </div>
                <div>
                    <label for="language">Язык (оставьте пустым для любого):</label>
                    <input type="text" id="language" placeholder="ru, en, es, etc.">
                </div>
                <div id="result"></div>
            </div>
            <script>
                async function getTranscript() {
                    const url = document.getElementById('videoUrl').value;
                    const language = document.getElementById('language').value || 'any';
                    const resultDiv = document.getElementById('result');
                    
                    if (!url) {
                        resultDiv.textContent = 'Пожалуйста, введите URL видео';
                        return;
                    }
                    
                    resultDiv.textContent = 'Загрузка...';
                    
                    try {
                        const response = await fetch(`/api/transcript?url=${encodeURIComponent(url)}&language=${language}`);
                        const data = await response.json();
                        
                        if (data.success) {
                            resultDiv.innerHTML = `
                                <h3>Транскрипт (${data.language}):</h3>
                                <p>${data.transcript.replace(/\n/g, '<br>')}</p>
                                <p><strong>Доступные языки:</strong> ${data.available_languages?.join(', ') || 'Неизвестно'}</p>
                            `;
                        } else {
                            resultDiv.textContent = `Ошибка: ${data.error}`;
                            if (data.available_languages?.length > 0) {
                                resultDiv.textContent += `\nДоступные языки: ${data.available_languages.join(', ')}`;
                            }
                        }
                    } catch (error) {
                        resultDiv.textContent = `Произошла ошибка: ${error.message}`;
                    }
                }
            </script>
        </body>
    </html>
    """

@app.get("/api/transcript")
async def api_get_transcript(
    request: Request,
    response: Response,
    url: str = Query(..., description="URL YouTube видео"),
    language: str = Query("any", description="Предпочитаемый язык (например, 'ru', 'en'), 'any' для любого доступного")
) -> Dict[str, Any]:
    """
    Получает транскрипт видео на любом доступном языке
    
    Аргументы:
        url (str): URL YouTube видео
        language (str, optional): Предпочитаемый язык. По умолчанию 'any' (любой доступный)
        
    Возвращает:
        dict: Словарь с транскриптом и метаданными
    """
    try:
        # Используем нашу функцию из сервиса
        result = get_transcript(url, language)
        
        # Устанавливаем правильный Content-Type для кириллицы
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        
        # Возвращаем результат
        if not result.get("success"):
            response.status_code = status.HTTP_404_NOT_FOUND
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {str(e)}", exc_info=True)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "success": False,
            "error": f"Внутренняя ошибка сервера: {str(e)}",
            "video_id": extract_video_id(url) or ""
        }

@app.get("/api/languages/{video_id}")
async def api_get_available_languages(
    video_id: str,
    response: Response
) -> Dict[str, Any]:
    """
    Получает список доступных языков для видео
    
    Аргументы:
        video_id (str): ID YouTube видео
        
    Возвращает:
        dict: Словарь со списком доступных языков
    """
    try:
        languages = get_available_languages(video_id)
        return {
            "success": True,
            "video_id": video_id,
            "languages": languages,
            "error": None
        }
    except Exception as e:
        logger.error(f"Ошибка при получении списка языков: {str(e)}", exc_info=True)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "success": False,
            "video_id": video_id,
            "languages": [],
            "error": f"Не удалось получить список языков: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_server_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
