from fastapi import FastAPI, Response, Query, status, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response as FastAPIResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union, Callable
import logging
import json
import ujson
import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

# Set default encoding to UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Custom JSON response class that handles encoding properly
class UnicodeJSONResponse(Response):
    media_type = "application/json"
    
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        background = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)
    
    def render(self, content: Any) -> bytes:
        try:
            # First try with ujson
            return ujson.dumps(
                content,
                ensure_ascii=False,
                escape_forward_slashes=False,
            ).encode('utf-8')
        except Exception as e:
            # Fall back to json with ensure_ascii=False
            return json.dumps(
                content,
                ensure_ascii=False,
                indent=None,
                separators=(",", ":"),
            ).encode('utf-8')

# Импортируем наш сервис транскрипции
from transcript_service import extract_video_id, get_available_languages

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

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница с формой для ввода URL"""
    return HTMLResponse(content=HTML_FORM, status_code=200)

class CustomJSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"
    
    def render(self, content: Any) -> bytes:
        return ujson.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            escape_forward_slashes=False,
        ).encode("utf-8")

def get_subtitles_with_yt_dlp(video_id: str, lang: str = 'ru') -> Dict[str, Any]:
    """Получает субтитры с помощью yt-dlp"""
    try:
        # Создаем временную директорию
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, f"{video_id}.%(ext)s")
        
        # Запускаем yt-dlp для получения субтитров
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--write-auto-sub',
            '--sub-format', 'vtt',
            '--sub-lang', lang,
            '--output', output_template,
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            raise Exception(f"yt-dlp error: {result.stderr}")
        
        # Ищем файл с субтитрами
        vtt_files = list(Path(temp_dir).glob(f"{video_id}*.{lang}.vtt"))
        if not vtt_files:
            raise Exception("Не удалось найти файл с субтитрами")
        
        # Читаем содержимое файла
        with open(vtt_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Удаляем временную директорию
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return {
            "success": True,
            "transcript": content,
            "language": lang,
            "is_generated": True
        }
        
    except Exception as e:
        # Убедимся, что временная директория удалена в случае ошибки
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise

@app.get("/api/transcript", response_class=UnicodeJSONResponse)
async def api_get_transcript(
    request: Request,
    url: str = Query(..., description="URL YouTube видео"),
    language: str = Query("ru", description="Предпочитаемый язык (например, 'ru', 'en')")
) -> Dict[str, Any]:
    """
    Получает транскрипт видео на указанном языке с помощью yt-dlp
    
    Аргументы:
        url (str): URL YouTube видео
        language (str, optional): Язык субтитров. По умолчанию 'ru'
        
    Возвращает:
        dict: Словарь с транскриптом и метаданными
    """
    try:
        # Извлекаем ID видео из URL
        video_id = extract_video_id(url)
        if not video_id:
            return {
                "success": False,
                "error": "Неверный URL YouTube видео"
            }
        
        # Получаем субтитры с помощью yt-dlp
        result = get_subtitles_with_yt_dlp(video_id, language)
        
        # Если успешно, возвращаем результат
        if result.get("success"):
            return {
                "success": True,
                "video_id": video_id,
                "transcript": result["transcript"],
                "language": result["language"],
                "is_generated": result.get("is_generated", False)
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Не удалось получить транскрипт"),
                "video_id": video_id
            }
            
    except Exception as e:
        logger.error(f"Ошибка при получении транскрипта: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Ошибка при обработке запроса: {str(e)}",
            "video_id": video_id if 'video_id' in locals() else None
        }

@app.get("/api/available-languages/{video_id}", response_class=UnicodeJSONResponse)
async def api_get_available_languages(
    request: Request,
    video_id: str
) -> Dict[str, Any]:
    """
    Заглушка для совместимости. 
    В реальности yt-dlp не предоставляет простого способа получить список доступных языков без загрузки субтитров.
    """
    try:
        # Возвращаем стандартный список языков, так как yt-dlp не предоставляет простого способа
        # получить список доступных языков без загрузки самих субтитров
        return {
            "success": True,
            "video_id": video_id,
            "languages": [
                {"code": "ru", "name": "Russian"},
                {"code": "en", "name": "English"}
            ],
            "note": "This is a static list. yt-dlp doesn't provide a simple way to get available languages without downloading subtitles."
        }
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка языков: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Ошибка при получении списка языков: {str(e)}",
            "video_id": video_id
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_server_clean:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
