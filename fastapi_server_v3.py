from fastapi import FastAPI, Request, Response, Query, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import json
import re
import ujson
import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import urllib.parse
import requests

# Set default encoding to UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Настройка логирования
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_formatter = logging.Formatter(log_format)

# Создаем логгер
logger = logging.getLogger('youtube_transcript')
logger.setLevel(logging.DEBUG)

# Обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_formatter)

# Обработчик для записи в файл
file_handler = logging.FileHandler('youtube_transcript_debug.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_formatter)

# Добавляем обработчики к логгеру
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Убираем дублирование логов
logger.propagate = False

# Enable debug logging for uvicorn
logging.getLogger('uvicorn').setLevel(logging.DEBUG)
logging.getLogger('uvicorn.error').setLevel(logging.DEBUG)
logging.getLogger('uvicorn.access').setLevel(logging.DEBUG)

# Create FastAPI instance
app = FastAPI(
    title="YouTube Transcript API v3",
    description="API для получения транскриптов YouTube видео с поддержкой yt-dlp",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug function to print all routes
def print_routes():
    logger.info("\nRegistered routes:")
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = ", ".join(getattr(route, "methods", []))
        name = getattr(route, "name", "")
        logger.info(f"- {path} [{methods}] (name: {name})")

def extract_video_id(url: str) -> Optional[str]:
    """Извлекает ID видео из URL YouTube"""
    import re
    patterns = [
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/live\/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def vtt_to_text(vtt_content: str) -> str:
    """
    Convert VTT content to clean text
    
    Args:
        vtt_content (str): VTT formatted content
        
    Returns:
        str: Cleaned text content
    """
    if not vtt_content:
        return ""
    
    lines = []
    for line in vtt_content.split('\n'):
        line = line.strip()
        # Skip empty lines and timestamps
        if not line or '-->' in line or line.lower() == 'webvtt':
            continue
        # Skip metadata
        if line.startswith(('Kind:', 'Language:', 'Style:', '##', 'NOTE')):
            continue
        # Skip line numbers
        if line.isdigit():
            continue
        lines.append(line)
    
    # Join lines with spaces
    text = ' '.join(lines)
    
    # Basic cleanup
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'\[.*?\]', '', text)  # Remove anything in brackets
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize spaces
    
    return text

def get_subtitles_with_yt_dlp(video_id: str, lang: str = "ru") -> str:
    """
    Получает субтитры для видео с помощью yt-dlp.
    Возвращает текст субтитров или None, если не удалось получить.
    """
    try:
        # Создаем временную директорию для файлов
        with tempfile.TemporaryDirectory() as temp_dir:
            # Формируем команду для получения субтитров
            cmd = [
                "yt-dlp",
                "--skip-download",
                "--write-auto-sub",
                "--sub-format", "vtt",
                "--sub-lang", lang,
                "--output", f"{temp_dir}/%(id)s.%(ext)s",
                "--no-warnings",
                "--no-playlist",
                "--force-ipv4",
                "--no-check-certificate",
                "--ignore-errors",
                "--no-continue",
                "--no-overwrites",
                "--no-part",
                "--no-mtime",
                f"https://www.youtube.com/watch?v={video_id}"
            ]
            
            # Запускаем yt-dlp для получения субтитров
            logger.debug(f"Выполнение команды: {' '.join(cmd)}")
            try:
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                # Логируем вывод команды
                if process.stdout:
                    logger.debug(f"Вывод команды (stdout): {process.stdout[:500]}...")
                if process.stderr:
                    logger.warning(f"Ошибки команды (stderr): {process.stderr[:500]}...")
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"Ошибка при выполнении yt-dlp: {e}")
                if hasattr(e, 'stdout') and e.stdout:
                    logger.error(f"Вывод команды (stdout): {e.stdout[:500]}...")
                if hasattr(e, 'stderr') and e.stderr:
                    logger.error(f"Вывод ошибок (stderr): {e.stderr[:500]}...")
                
                # Пробуем английские субтитры, если запрошенный язык не найден
                if "language is not available" in str(e).lower() and lang != "en":
                    logger.info("Пробуем английские субтитры...")
                    return get_subtitles_with_yt_dlp(video_id, "en")
                return None
            
            # Ищем файл с субтитрами
            sub_files = list(Path(temp_dir).glob(f"*.vtt")) + list(Path(temp_dir).glob(f"*.srt"))
            if not sub_files:
                logger.warning(f"Файлы субтитров не найдены в {temp_dir}")
                return None
                
            vtt_file = sub_files[0]  # Берем первый найденный файл
            logger.debug(f"Найден файл субтитров: {vtt_file}")
            
            # Читаем содержимое файла
            try:
                with open(vtt_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if not content.strip():
                        logger.warning("Файл субтитров пуст")
                        return None
                    
                    # Обрабатываем содержимое субтитров
                    lines = []
                    for line in content.split('\n'):
                        line = line.strip()
                        # Пропускаем пустые строки, временные метки и заголовки
                        if not line or '-->' in line or line.lower().startswith(('webvtt', 'kind:', 'language:')):
                            continue
                        # Пропускаем номера строк и служебную информацию
                        if line.isdigit() or line.startswith('NOTE') or line.startswith('STYLE'):
                            continue
                        lines.append(line)
                    
                    # Объединяем строки в один текст
                    transcript = ' '.join(lines)
                    
                    # Если транскрипт слишком короткий, возможно, это список языков
                    if len(transcript.split()) < 10 and any(word in transcript.lower() for word in ['language', 'available', 'subtitle']):
                        logger.warning(f"Обнаружен подозрительно короткий транскрипт: {transcript}")
                        return None
                    
                    # Удаляем лишние пробелы и символы
                    import re
                    transcript = re.sub(r'\[.*?\]', '', transcript)  # удаляем текст в квадратных скобках
                    transcript = re.sub(r'<.*?>', '', transcript)      # удаляем HTML-теги
                    transcript = re.sub(r'[^\w\s.,!?-]', ' ', transcript)  # оставляем только буквы, цифры и основные знаки препинания
                    transcript = re.sub(r'\s+', ' ', transcript).strip()  # удаляем лишние пробелы
                    
                    if not transcript:
                        logger.warning("После очистки транскрипт пуст")
                        return None
                        
                    return transcript
                    
            except Exception as e:
                logger.error(f"Ошибка при чтении файла субтитров: {e}", exc_info=True)
                return None
                
            logger.debug("Функция get_subtitles_with_yt_dlp завершена")
            return transcript
                
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении субтитров: {str(e)}", exc_info=True)
        return None

# HTML интерфейс для тестирования
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Transcript API v3</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { margin-top: 20px; }
        input[type="text"] { width: 70%; padding: 10px; margin-right: 10px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        #result { margin-top: 20px; white-space: pre-wrap; border: 1px solid #ddd; padding: 10px; }
        .loading { color: #666; font-style: italic; }
        .error { color: #d32f2f; }
        .success { color: #388e3c; }
    </style>
</head>
<body>
    <div class="container">
        <h1>YouTube Transcript API v3</h1>
        <p>Введите URL YouTube видео, чтобы получить его транскрипт:</p>
        <div>
            <input type="text" id="videoUrl" placeholder="https://www.youtube.com/watch?v=...">
            <button onclick="getTranscript()">Получить транскрипт</button>
        </div>
        <div style="margin-top: 10px;">
            <label for="language">Язык (по умолчанию 'ru'):</label>
            <input type="text" id="language" placeholder="ru" value="ru">
        </div>
        <div id="result" class="loading">Введите URL и нажмите кнопку</div>
    </div>
    <script>
        async function getTranscript() {
            const url = document.getElementById('videoUrl').value;
            const language = document.getElementById('language').value || 'ru';
            const resultDiv = document.getElementById('result');
            
            if (!url) {
                resultDiv.textContent = 'Пожалуйста, введите URL видео';
                resultDiv.className = 'error';
                return;
            }
            
            resultDiv.textContent = 'Загрузка...';
            resultDiv.className = 'loading';
            
            try {
                const response = await fetch(`/api/transcript?url=${encodeURIComponent(url)}&language=${language}`);
                const data = await response.json();
                
                if (data.success) {
                    // Format the transcript with proper line breaks
                    const formattedTranscript = data.transcript
                        .replace(/\r\n/g, '\n')  // Normalize line endings
                        .replace(/\n/g, '<br>')    // Convert newlines to <br>
                        .replace(/<br><br>/g, '<br>\n<br>');  // Add extra line breaks between paragraphs
                    
                    resultDiv.innerHTML = `
                        <h3>Транскрипт (${data.language}):</h3>
                        <div style="max-height: 500px; overflow-y: auto; border: 1px solid #eee; padding: 10px; white-space: pre-line;">
                            ${formattedTranscript}
                        </div>
                        <p><small>Формат: ${data.format || 'неизвестно'}</small></p>
                    `;
                    resultDiv.className = 'success';
                } else {
                    resultDiv.textContent = `Ошибка: ${data.error || 'Неизвестная ошибка'}`;
                    resultDiv.className = 'error';
                }
            } catch (error) {
                resultDiv.textContent = `Произошла ошибка: ${error.message}`;
                resultDiv.className = 'error';
                console.error('Ошибка при получении транскрипта:', error);
            }
        }
    </script>
</body>
</html>
"""

@app.get("/routes")
async def list_routes():
    """List all available routes (for debugging)"""
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": getattr(route, "methods", None)
        })
    return {"routes": routes}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница с формой для ввода URL"""
    return HTMLResponse(content=HTML_FORM, status_code=200)

@app.get("/api/transcript")
async def api_get_transcript(
    request: Request,
    response: Response,
    url: str = Query(..., description="URL YouTube видео"),
    language: str = Query("ru", description="Язык субтитров (например, 'ru', 'en')")
) -> Response:
    """
    Получает транскрипт видео с YouTube.
    Возвращает текст субтитров в указанном языке.
    """
    try:
        # Извлекаем ID видео из URL
        video_id = extract_video_id(url)
        if not video_id:
            return PlainTextResponse("Неверный URL YouTube", status_code=400)
            
        logger.info(f"Запрос транскрипта для видео {video_id} на языке {language}")
        
        # Получаем субтитры
        transcript = get_subtitles_with_yt_dlp(video_id, language)
        
        # Если субтитры не найдены, пробуем английский как запасной вариант
        if not transcript and language != 'en':
            logger.warning(f"Субтитры на языке {language} не найдены, пробуем английский...")
            transcript = get_subtitles_with_yt_dlp(video_id, 'en')
        
        if not transcript:
            return PlainTextResponse(
                "Не удалось получить субтитры для данного видео. "
                "Попробуйте изменить язык или проверьте другое видео.",
                status_code=404
            )
        
        # Логируем первые 200 символов транскрипта для отладки
        logger.info(f"Успешно получен транскрипт (первые 200 символов): {transcript[:200]}...")
        
        # Дополнительная очистка текста
        import re
        
        # Удаляем HTML-теги и лишние символы
        transcript = re.sub(r'<[^>]+>', '', transcript)  # Удаляем HTML-теги
        transcript = re.sub(r'\[.*?\]', '', transcript)  # Удаляем текст в квадратных скобках
        transcript = re.sub(r'\s+', ' ', transcript).strip()  # Заменяем множественные пробелы на один
        
        # Возвращаем результат в кодировке UTF-8 для корректного отображения кириллицы
        return PlainTextResponse(
            transcript,
            media_type="text/plain; charset=utf-8"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении транскрипта: {e}", exc_info=True)
        return PlainTextResponse(
            f"Произошла ошибка: {str(e)}",
            status_code=500,
            media_type="text/plain; charset=utf-8"
        )

@app.get("/api/available-languages/{video_id}")
async def api_get_available_languages(
    video_id: str,
    response: Response
) -> Dict[str, Any]:
    """
    Возвращает список поддерживаемых языков для субтитров.
    
    ВНИМАНИЕ: yt-dlp не предоставляет простого способа получить список доступных языков
    без загрузки субтитров, поэтому возвращаем статический список наиболее распространенных языков.
    """
    try:
        # Список наиболее распространенных языков с их кодами и названиями
        common_languages = [
            {"code": "ru", "name": "Русский"},
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Español"},
            {"code": "fr", "name": "Français"},
            {"code": "de", "name": "Deutsch"},
            {"code": "it", "name": "Italiano"},
            {"code": "pt", "name": "Português"},
            {"code": "ja", "name": "日本語"},
            {"code": "ko", "name": "한국어"},
            {"code": "zh-Hans", "name": "中文(简体)"},
            {"code": "zh-Hant", "name": "中文(繁體)"},
            {"code": "ar", "name": "العربية"},
            {"code": "hi", "name": "हिन्दी"},
            {"code": "bn", "name": "বাংলা"},
            {"code": "pa", "name": "ਪੰਜਾਬੀ"},
            {"code": "tr", "name": "Türkçe"},
            {"code": "vi", "name": "Tiếng Việt"},
            {"code": "th", "name": "ไทย"},
            {"code": "id", "name": "Bahasa Indonesia"},
            {"code": "nl", "name": "Nederlands"},
            {"code": "pl", "name": "Polski"},
            {"code": "uk", "name": "Українська"},
            {"code": "el", "name": "Ελληνικά"},
            {"code": "cs", "name": "Čeština"},
            {"code": "sv", "name": "Svenska"},
            {"code": "da", "name": "Dansk"},
            {"code": "fi", "name": "Suomi"},
            {"code": "no", "name": "Norsk"},
            {"code": "hu", "name": "Magyar"},
            {"code": "ro", "name": "Română"},
            {"code": "sk", "name": "Slovenčina"},
            {"code": "bg", "name": "Български"},
            {"code": "sr", "name": "Српски"},
            {"code": "hr", "name": "Hrvatski"},
            {"code": "sl", "name": "Slovenščina"},
            {"code": "he", "name": "עברית"},
            {"code": "fa", "name": "فارسی"},
            {"code": "ur", "name": "اردو"},
            {"code": "ms", "name": "Bahasa Melayu"},
            {"code": "fil", "name": "Filipino"},
            {"code": "sw", "name": "Kiswahili"}
        ]
        
        return {
            "success": True,
            "video_id": video_id,
            "languages": common_languages,
            "note": "This is a static list of the most common languages. yt-dlp doesn't provide a simple way to get available languages without downloading subtitles."
        }
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка языков: {str(e)}", exc_info=True)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "success": False,
            "video_id": video_id,
            "error": f"Не удалось получить список языков: {str(e)}"
        }

# Print all registered routes
print_routes()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_server_v3:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
