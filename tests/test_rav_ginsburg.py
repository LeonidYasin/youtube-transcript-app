import asyncio
import httpx
import json
from datetime import datetime
from typing import List, Dict, Optional

# Базовый URL нашего FastAPI приложения
BASE_URL = "http://localhost:8000"

async def поиск_канала(название_канала: str = "Рав Гинзбург"):
    """Тестирование поиска канала рава Гинзбурга"""
    print(f"\n{'='*50}")
    print(f"Тестирование поиска канала: {название_канала}")
    print("="*50)
    
    async with httpx.AsyncClient() as клиент:
        try:
            # Тестируем эндпоинт поиска канала
            ответ = await клиент.get(
                f"{BASE_URL}/api/channel/",
                params={"channel_name": название_канала, "limit": 5}
            )
            
            if ответ.status_code != 200:
                print(f"Ошибка: {ответ.status_code} - {ответ.text}")
                return None
                
            данные_канала = ответ.json()
            print(f"Найден канал: {данные_канала.get('channel_name')}")
            print(f"ID канала: {данные_канала.get('channel_id')}")
            print(f"Найдено видео: {len(данные_канала.get('videos', []))}")
            
            return данные_канала
            
        except Exception as e:
            print(f"Ошибка при поиске канала: {str(e)}")
            return None

async def поиск_видео(запрос: str, лимит: int = 5):
    """Тестирование поиска видео"""
    print(f"\n{'='*50}")
    print(f"Тестирование поиска видео по запросу: {запрос}")
    print("="*50)
    
    async with httpx.AsyncClient() as клиент:
        try:
            ответ = await клиент.get(
                f"{BASE_URL}/api/search/",
                params={"query": запрос, "limit": лимит}
            )
            
            if ответ.status_code != 200:
                print(f"Ошибка: {ответ.status_code} - {ответ.text}")
                return None
                
            видео = ответ.json()
            print(f"Найдено видео: {len(видео)}")
            
            for i, видео in enumerate(видео, 1):
                print(f"\n{i}. {видео.get('title')}")
                print(f"   Канал: {видео.get('channel')}")
                print(f"   Длительность: {видео.get('duration')}")
                print(f"   Просмотры: {видео.get('view_count')}")
                print(f"   Ссылка: https://www.youtube.com/watch?v={видео.get('video_id')}")
            
            return видео
            
        except Exception as e:
            print(f"Ошибка при поиске видео: {str(e)}")
            return None

async def тест_транскрипта(ссылка_на_видео: str, язык: str = "ru"):
    """Тестирование извлечения транскрипта для видео"""
    print(f"\n{'='*50}")
    print(f"Тестирование извлечения транскрипта для: {ссылка_на_видео}")
    print("="*50)
    
    async with httpx.AsyncClient() as клиент:
        try:
            ответ = await клиент.get(
                f"{BASE_URL}/api/transcript/",
                params={"url": ссылка_на_видео, "language": язык}
            )
            
            if ответ.status_code != 200:
                print(f"Ошибка: {ответ.status_code} - {ответ.text}")
                return None
                
            данные_транскрипта = ответ.json()
            print(f"Язык: {данные_транскрипта.get('language')}")
            print(f"Автогенерируемый: {данные_транскрипта.get('is_auto_generated')}")
            print(f"Длина транскрипта: {len(данные_транскрипта.get('transcript', ''))} символов")
            
            # Выводим первые 200 символов транскрипта
            предпросмотр = данные_транскрипта.get('transcript', '')[:200]
            if len(данные_транскрипта.get('transcript', '')) > 200:
                предпросмотр += "..."
            print(f"\nПредпросмотр транскрипта:\n{предпросмотр}")
            
            return данные_транскрипта
            
        except Exception as e:
            print(f"Ошибка при извлечении транскрипта: {str(e)}")
            return None

async def полный_тест(название_канала: str = "Рав Гинзбург", лимит: int = 3):
    """Полный тест: поиск канала, получение видео, извлечение транскриптов"""
    print("\n" + "="*50)
    print("НАЧАЛО ПОЛНОГО ТЕСТА")
    print("="*50)
    
    # Шаг 1: Находим канал
    данные_канала = await поиск_канала(название_канала)
    if not данные_канала or not данные_канала.get('videos'):
        print("Канал или видео не найдены, завершение...")
        return
        
    # Шаг 2: Тестируем извлечение транскриптов для каждого видео (до лимита)
    результаты = []
    for i, видео in enumerate(данные_канала['videos'][:лимит], 1):
        ссылка_на_видео = f"https://www.youtube.com/watch?v={видео['video_id']}"
        print(f"\nТестирование видео {i}/{min(лимит, len(данные_канала['videos']))}: {видео['title']}")
        
        # Сначала пробуем на русском
        транскрипт = await тест_транскрипта(ссылка_на_видео, "ru")
        
        # Если на русском нет, пробуем английский
        if not транскрипт or not транскрипт.get('transcript'):
            print("Русский транскрипт не найден, пробуем английский...")
            транскрипт = await тест_транскрипта(ссылка_на_видео, "en")
            
        # Сохраняем результаты
        результаты.append({
            "video_id": видео['video_id'],
            "title": видео['title'],
            "has_transcript": bool(транскрипт and транскрипт.get('transcript')),
            "language": транскрипт.get('language') if транскрипт else None,
            "transcript_length": len(транскрипт.get('transcript', '')) if транскрипт else 0
        })
    
    # Выводим итоги
    print("\n" + "="*50)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*50)
    print(f"Канал: {данные_канала.get('channel_name')}")
    print(f"Проверено видео: {len(результаты)}")
    print(f"Видео с транскриптами: {sum(1 for r in результаты if r['has_transcript'])}")
    
    # Сохраняем подробные результаты в файл
    метка_времени = datetime.now().strftime("%Y%m%d_%H%M%S")
    имя_файла = f"результаты_теста_{метка_времени}.json"
    with open(имя_файла, "w", encoding="utf-8") as файл:
        json.dump({
            "channel": данные_канала.get('channel_name'),
            "channel_id": данные_канала.get('channel_id'),
            "test_date": datetime.now().isoformat(),
            "videos_tested": len(результаты),
            "videos_with_transcripts": sum(1 for r in результаты if r['has_transcript']),
            "results": результаты
        }, файл, ensure_ascii=False, indent=2)
    
    print(f"\nПодробные результаты сохранены в файл: {имя_файла}")

async def main():
    # Тестируем отдельные эндпоинты
    await поиск_канала("Рав Гинзбург")
    await поиск_видео("рав гинзбург лекция", 3)
    
    # Тестируем полный цикл с одним видео
    тестовая_ссылка = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Тестовое видео
    await тест_транскрипта(тестовая_ссылка)
    
    # Раскомментируйте для тестирования полного цикла с видео канала
    # await полный_тест("Рав Гинзбург", 3)

if __name__ == "__main__":
    asyncio.run(main())
