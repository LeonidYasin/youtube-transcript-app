from fastapi import FastAPI, Request, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, RequestBlocked
import logging
import uvicorn
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, HttpUrl
from enum import Enum

# Настройка логирования с правильной кодировкой
import codecs

# Удаляем существующие обработчики логов (если есть)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Настраиваем форматтер
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Настраиваем обработчик для файла с кодировкой UTF-8
file_handler = logging.FileHandler('youtube_fastapi.log', mode='w', encoding='utf-8')
file_handler.setFormatter(formatter)

# Настраиваем обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Настраиваем корневой логгер
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

class TranscriptLanguage(str, Enum):
    RU = "ru"
    EN = "en"
    ANY = "any"

class TranscriptResponse(BaseModel):
    success: bool
    video_id: str
    transcript: Optional[str] = None
    error: Optional[str] = None

app = FastAPI(
    title="YouTube Transcript API",
    description="API для получения транскриптов YouTube видео",
    version="1.0.0",
    docs_url=None,  # Отключаем стандартную документацию
    redoc_url=None
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка шаблонов
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Создаем директорию для шаблонов, если её нет
(BASE_DIR / "templates").mkdir(exist_ok=True)

# Создаем шаблон HTML
with open(BASE_DIR / "templates" / "index.html", "w", encoding="utf-8") as f:
    f.write("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Transcript</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px;
                line-height: 1.6;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px;
            }
            h1 { 
                color: #d32f2f; 
                text-align: center;
            }
            .form-group {
                margin-bottom: 20px;
            }
            input[type="text"] {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                background: #d32f2f;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background: #b71c1c;
            }
            #result {
                margin-top: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-height: 100px;
                white-space: pre-wrap;
            }
            .error {
                color: #d32f2f;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>YouTube Transcript</h1>
            <div class="form-group">
                <label for="videoUrl">Введите URL видео с YouTube:</label>
                <input type="text" id="videoUrl" value="https://www.youtube.com/watch?v=7CmkwhWqUzE" placeholder="Вставьте URL видео">
                <button onclick="getTranscript()">Получить транскрипт</button>
            </div>
            <div id="result"></div>
        </div>
        <script>
        async function getTranscript() {
            const url = document.getElementById('videoUrl').value;
            const resultDiv = document.getElementById('result');
            
            if (!url) {
                resultDiv.innerHTML = '<div class="error">Пожалуйста, введите URL видео</div>';
                return;
            }
            
            resultDiv.innerHTML = 'Загружаем транскрипт...';
            
            try {
                const response = await fetch(`/api/transcript?url=${encodeURIComponent(url)}`);
                const data = await response.json();
                
                if (data.transcript) {
                    resultDiv.textContent = data.transcript;
                } else if (data.error) {
                    resultDiv.innerHTML = `<div class="error">${data.error}</div>`;
                } else {
                    resultDiv.innerHTML = '<div class="error">Транскрипт не найден</div>';
                }
            } catch (error) {
                console.error('Ошибка:', error);
                resultDiv.innerHTML = `<div class="error">Ошибка: ${error.message}</div>`;
            }
        }
        </script>
    </body>
    </html>
    """)

def extract_video_id(url: str) -> str:
    """Извлекает ID видео из URL YouTube."""
    if not url:
        return ""
    
    try:
        # Удаляем все параметры после & и лишние символы
        clean_url = url.split('&')[0].strip()
        
        # Обработка коротких ссылок youtu.be
        if 'youtu.be' in clean_url:
            video_id = clean_url.split('/')[-1].split('?')[0]
            return video_id if video_id and len(video_id) == 11 else ""
            
        # Обработка обычных ссылок YouTube
        parsed_url = urlparse(clean_url)
        if 'youtube.com' in parsed_url.netloc:
            if parsed_url.path == '/watch':
                video_id = parse_qs(parsed_url.query).get('v', [''])[0]
                return video_id if video_id and len(video_id) == 11 else ""
            elif parsed_url.path.startswith('/embed/'):
                video_id = parsed_url.path.split('/')[2]
                return video_id if video_id and len(video_id) == 11 else ""
                
        return ""
    except Exception as e:
        logger.error(f"Ошибка при извлечении ID видео из URL {url}: {str(e)}")
        return ""

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Документация Swagger UI
@app.get("/docs", include_in_schema=False)
async def get_documentation():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="YouTube Transcript API - Документация",
        swagger_favicon_url="https://www.youtube.com/favicon.ico"
    )

# OpenAPI схема
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_json():
    openapi_schema = get_openapi(
        title="YouTube Transcript API",
        version="1.0.0",
        description="API для получения транскриптов YouTube видео",
        routes=app.routes,
    )
    return JSONResponse(openapi_schema)

# API Endpoint для получения транскрипта
@app.get(
    "/api/transcript",
    response_model=TranscriptResponse,
    summary="Получить транскрипт видео",
    description="""
    Получает транскрипт YouTube видео по его URL.
    Поддерживает как полные URL, так и короткие (youtu.be).
    """,
    responses={
        200: {"description": "Транскрипт успешно получен"},
        400: {"description": "Неверный URL или параметры запроса"},
        403: {"description": "Для этого видео отключены субтитры"},
        404: {"description": "Видео или транскрипт не найдены"},
        429: {"description": "Превышено количество запросов"},
        500: {"description": "Внутренняя ошибка сервера"}
    }
)
async def get_transcript(
    request: Request,
    response: Response,
    url: str = Query(..., description="YouTube video URL"),
    language: str = Query('any', description="Preferred language code (e.g., 'ru', 'en'), or 'any' for first available")
):
    logger.info(f"Получен запрос на получение транскрипта для видео: {url}")
    
    try:
        # Извлекаем ID видео из URL
        video_id = extract_video_id(url)
        if not video_id:
            error_msg = "Не удалось извлечь ID видео из URL"
            logger.error(f"{error_msg}: {url}")
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"success": False, "error": error_msg}
            
        logger.info(f"Извлечен ID видео: {video_id}")
        
        try:
            logger.info(f"Попытка получения списка доступных транскриптов для видео {video_id}")
            
            # Пробуем получить список транскриптов
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                logger.info(f"Доступные транскрипты: {[t.language_code for t in transcript_list]}")
            except Exception as e:
                logger.error(f"Ошибка при получении списка транскриптов: {str(e)}", exc_info=True)
                raise Exception(f"Не удалось получить список доступных транскриптов: {str(e)}")
            
            # Функция для получения списка доступных языков
            def get_available_languages(transcript_list):
                try:
                    return [{
                        'code': t.language_code,
                        'is_generated': t.is_generated,
                        'is_translatable': t.is_translatable,
                        'language': t.language
                    } for t in transcript_list]
                except Exception as e:
                    logger.warning(f"Не удалось получить список языков: {str(e)}")
                    return []

            # Пробуем получить список доступных транскриптов
            try:
                available_languages = get_available_languages(transcript_list)
                logger.info(f"Доступные языки: {available_languages}")
                
                # Пробуем получить транскрипт напрямую с разными вариантами языка
                language_variants = []
                if language == 'ru':
                    # Для русского пробуем разные варианты кодов
                    language_variants = ['ru', 'ru-RU', 'ru-UA', 'be', 'uk', 'kk']
                else:
                    language_variants = [language, language.split('-')[0]]
                
                # Добавляем английский как запасной вариант, если это не русский
                if language != 'en' and language != 'ru':
                    language_variants.extend(['en', 'en-US', 'en-GB'])
                
                # Удаляем дубликаты и пустые значения
                language_variants = list(dict.fromkeys([l for l in language_variants if l]))
                
                logger.info(f"Попытка получить транскрипт напрямую для языков: {language_variants}")
                
                try:
                    # Get the transcript and detect the actual language
                    transcript = YouTubeTranscriptApi.get_transcript(
                        video_id, 
                        languages=language_variants,
                        preserve_formatting=True
                    )
                    
                    # Extract the actual language code from the transcript if available
                    detected_language = None
                    if transcript and len(transcript) > 0:
                        # Try to detect language from the first few lines
                        sample_text = " ".join([t['text'] for t in transcript[:5]])
                        # Simple language detection based on character sets
                        if any(c >= 'а' and c <= 'я' or c >= 'А' and c <= 'Я' for c in sample_text):
                            detected_language = 'ru'
                        elif any(c >= 'a' and c <= 'z' or c >= 'A' and c <= 'Z' for c in sample_text):
                            detected_language = 'en'
                    
                    # Use detected language or fallback to requested language
                    result_language = detected_language or language_variants[0]
                    transcript_text = "\n".join([t['text'] for t in transcript])
                    logger.info(f"Успешно получен транскрипт на языке {result_language}, символов: {len(transcript_text)}")
                    
                    response.headers["Content-Type"] = "application/json; charset=utf-8"
                    return {
                        "success": True,
                        "video_id": video_id,
                        "transcript": transcript_text,
                        "language": result_language,
                        "available_languages": [l['code'] for l in available_languages],
                        "error": None
                    }
                    
                except Exception as e:
                    logger.warning(f"Не удалось получить транскрипт напрямую: {str(e)}")
                    
                    # Try to get English as fallback
                    if language != 'en':
                        logger.info("Trying to get English transcript as fallback")
                        try:
                            # First try with manual transcripts
                            try:
                                transcript = YouTubeTranscriptApi.get_transcript(
                                    video_id,
                                    languages=['en'],
                                    preserve_formatting=True
                                )
                            except:
                                # If manual fails, try with generated
                                transcript = YouTubeTranscriptApi.get_transcript(
                                    video_id,
                                    languages=['en'],
                                    preserve_formatting=True
                                )
                            
                            if transcript:
                                transcript_text = "\n".join([t['text'] for t in transcript])
                                logger.info(f"Successfully got English transcript, {len(transcript_text)} characters")
                                
                                response.headers["Content-Type"] = "application/json; charset=utf-8"
                                return {
                                    "success": True,
                                    "video_id": video_id,
                                    "transcript": transcript_text,
                                    "language": "en",
            except Exception as e:
                logger.error(f"Ошибка при обработке списка языков: {str(e)}")
                try:
                    # Try one last time with default settings
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    if transcript:
                        transcript_text = "\n".join([t['text'] for t in transcript])
                        logger.info(f"Got transcript with default settings, {len(transcript_text)} characters")
                        
                        # Try to detect language from content
                        detected_lang = 'en'  # Default to English
                        sample = transcript_text.lower()
                        if any(cyr in sample for cyr in ['а', 'б', 'в', 'г', 'д', 'е']):
                            detected_lang = 'ru'
                        
                        response.headers["Content-Type"] = "application/json; charset=utf-8"
                        return {
                            "success": True,
                            "video_id": video_id,
                            "transcript": transcript_text,
                            "language": detected_lang,
                            "is_auto_detected": True,
                            "error": None
                        }
                except Exception as e2:
                    logger.error(f"Final fallback failed: {str(e2)}")
                
                available_languages = []
                
                # Если все попытки не удались, возвращаем ошибку с информацией о доступных языках
                available_languages = get_available_languages(transcript_list)
                    available_languages = get_available_languages(transcript_list)
                    
                    # Пробуем найти ручной транскрипт с учетом вариантов языка
                    found = False
                    for lang_variant in language_variants:
                        try:
                            transcript = transcript_list.find_manually_created_transcript([lang_variant])
                            logger.info(f"Найден ручной транскрипт на языке: {transcript.language_code}")
                            found = True
                            break
                        except Exception as e:
                            logger.debug(f"Не удалось найти ручной транскрипт для {lang_variant}: {str(e)}")
                            continue
                    
                    if not found:
                        logger.info("Ручной транскрипт не найден, пробуем автоматический")
                        # Пробуем найти автоматический транскрипт
                        for lang_variant in language_variants:
                            try:
                                transcript = transcript_list.find_generated_transcript([lang_variant])
                                logger.info(f"Найден автоматически сгенерированный транскрипт на языке: {transcript.language_code}")
                                found = True
                                break
                            except Exception as e:
                                logger.debug(f"Не удалось найти автоматический транскрипт для {lang_variant}: {str(e)}")
                                continue
                    
                    if not found and language != 'en':
                        logger.info("Пробуем найти английский транскрипт как запасной вариант")
                        # Пробуем найти английский как запасной вариант
                        try:
                            transcript = transcript_list.find_manually_created_transcript(['en', 'en-US', 'en-GB'])
                            logger.info(f"Найден английский ручной транскрипт: {transcript.language_code}")
                            found = True
                        except:
                            try:
                                transcript = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB'])
                                logger.info(f"Найден английский автоматический транскрипт: {transcript.language_code}")
                                found = True
                            except Exception as e:
                                logger.debug(f"Не удалось найти английский транскрипт: {str(e)}")
                    
                    if not found:
                        # Пробуем найти любой доступный транскрипт
                        try:
                            transcript = next(iter(transcript_list))
                            logger.info(f"Используем первый доступный транскрипт на языке: {transcript.language_code}")
                            found = True
                        except Exception as e:
                            logger.error(f"Не удалось найти ни одного транскрипта: {str(e)}")
                            error_msg = "Не удалось найти подходящий транскрипт. "
                            if available_languages:
                                error_msg += f"Доступные языки: {', '.join([f'{l['code']} ({l['language']})' for l in available_languages])}"
                            else:
                                error_msg += "Нет доступных транскриптов для этого видео."
                            raise Exception(error_msg)
                    
                    # Пробуем перевести, если нужно
                    if transcript.language_code != language:
                        try:
                            transcript = transcript.translate(language)
                            logger.info(f"Переведено на язык: {language}")
                        except Exception as e:
                            logger.warning(f"Не удалось перевести на {language}: {str(e)}")
                    
                    # Получаем текст транскрипта
                    transcript_text = "\n".join([t['text'] for t in transcript.fetch()])
                    logger.info(f"Успешно получен транскрипт, символов: {len(transcript_text)}")
                    
                except Exception as e:
                    logger.error(f"Ошибка при получении транскрипта: {str(e)}", exc_info=True)
                    raise Exception(f"Не удалось получить транскрипт: {str(e)}")
                
            
            # Добавляем пометку о языке и переводе, если нужно
            if used_translation:
                transcript_text = f"[Переведено с {transcript.language_code}]\n\n{transcript_text}"
            
            logger.info(f"Успешно получен транскрипт для видео {video_id}")
            response.headers["Content-Type"] = "application/json; charset=utf-8"
            return {
                "success": True,
                "video_id": video_id,
                "transcript": transcript_text,
                "error": None
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ошибка при получении транскрипта для видео {video_id}: {error_msg}", exc_info=True)
            
            # Более информативные сообщения об ошибках
            if "No transcripts found" in error_msg or "No transcript available" in error_msg:
                error_msg = "Для этого видео нет доступных транскриптов."
            elif "TranscriptsDisabled" in error_msg:
                error_msg = "Для этого видео отключены субтитры."
            elif "VideoUnavailable" in error_msg:
                error_msg = "Видео не найдено или недоступно."
            elif "Could not retrieve a transcript" in error_msg:
                error_msg = "Не удалось получить транскрипт для этого видео. Возможно, для него не включены субтитры."
            else:
                error_msg = f"Не удалось получить транскрипт: {error_msg}"
            
            response.headers["Content-Type"] = "application/json; charset=utf-8"
            return {
                "success": False,
                "video_id": video_id,
                "error": error_msg
            }
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Критическая ошибка: {error_msg}", exc_info=True)
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return {
            "success": False,
            "video_id": video_id if 'video_id' in locals() else "",
            "error": f"Произошла внутренняя ошибка сервера: {error_msg}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
