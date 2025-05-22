import os
import json
import time
import requests
from typing import List, Dict, Optional

# Configuration
CHANNEL_ID = "UC2Tf83L8T9MvWZ7XpVhQfRw"  # Rabbi Ginsburg's channel ID
API_KEY = os.getenv("YOUTUBE_API_KEY")  # You'll need to set this environment variable
RESULTS_PER_PAGE = 50  # Maximum allowed by YouTube API
TOTAL_VIDEOS = 100
OUTPUT_FILE = "rav_ginsburg_test_results.json"
BASE_API_URL = "http://localhost:8000/api/transcript"

def get_channel_videos(api_key: str, channel_id: str, max_results: int = 50) -> List[Dict]:
    """Get list of videos from a channel"""
    videos = []
    next_page_token = None
    
    while len(videos) < max_results:
        url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults={min(RESULTS_PER_PAGE, max_results - len(videos))}"
        
        if next_page_token:
            url += f"&pageToken={next_page_token}"
        
        response = requests.get(url)
        data = response.json()
        
        if 'items' not in data:
            print(f"Error fetching videos: {data}")
            break
            
        # Filter out non-video items (like playlists)
        videos.extend([
            {
                'video_id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'published_at': item['snippet']['publishedAt']
            }
            for item in data['items'] 
            if item['id']['kind'] == 'youtube#video'
        ])
        
        next_page_token = data.get('nextPageToken')
        if not next_page_token or len(videos) >= max_results:
            break
    
    return videos[:max_results]

def test_video_transcript(video_id: str, title: str) -> Dict:
    """Test transcript retrieval for a single video"""
    result = {
        'video_id': video_id,
        'title': title,
        'success': False,
        'error': None,
        'language': None,
        'is_auto_generated': False,
        'response_time': None,
        'response_length': 0
    }
    
    try:
        start_time = time.time()
        response = requests.get(
            BASE_API_URL,
            params={"url": f"https://www.youtube.com/watch?v={video_id}"},
            timeout=30  # 30 seconds timeout
        )
        result['response_time'] = time.time() - start_time
        
        if response.status_code == 200:
            result['success'] = True
            result['response_length'] = len(response.text)
            result['language'] = response.headers.get('X-Subtitles-Language')
            result['is_auto_generated'] = 'X-Subtitles-Auto-Generated' in response.headers
        else:
            result['error'] = f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

def generate_report(results: List[Dict]) -> str:
    """Generate a detailed report in Russian"""
    total_videos = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total_videos - successful
    
    # Calculate average response time
    response_times = [r['response_time'] for r in results if r['response_time'] is not None]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Count languages
    languages = {}
    for r in results:
        if r['language']:
            lang = r['language']
            if '(auto-generated)' in lang:
                lang = lang.replace(' (auto-generated)', ' (авто)')
            languages[lang] = languages.get(lang, 0) + 1
    
    # Generate report
    report = [
        "=" * 80,
        "ОТЧЁТ О ТЕСТИРОВАНИИ ТРАНСКРИПТОВ КАНАЛА РАВА ГИНЗБУРГА",
        "=" * 80,
        f"Всего протестировано видео: {total_videos}",
        f"Успешно получено транскриптов: {successful} ({successful/total_videos*100:.1f}%)",
        f"Не удалось получить: {failed} ({failed/total_videos*100:.1f}%)",
        f"Среднее время ответа: {avg_response_time:.2f} секунд",
        "",
        "Распределение по языкам:",
    ]
    
    for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
        report.append(f"- {lang}: {count} видео ({count/total_videos*100:.1f}%)")
    
    # Add failed cases details
    if failed > 0:
        report.extend([
            "",
            "Видео, для которых не удалось получить транскрипт:",
        ])
        for r in results:
            if not r['success']:
                report.append(f"- {r['title']} (ID: {r['video_id']}): {r['error']}")
    
    return "\n".join(report)

def main():
    # Check if API key is set
    if not API_KEY:
        print("ОШИБКА: Не задан API ключ YouTube Data API.")
        print("Пожалуйста, установите переменную окружения YOUTUBE_API_KEY")
        return
    
    print(f"Получение списка последних {TOTAL_VIDEOS} видео с канала...")
    try:
        videos = get_channel_videos(API_KEY, CHANNEL_ID, TOTAL_VIDEOS)
        print(f"Найдено {len(videos)} видео. Начинаю тестирование...")
        
        results = []
        for i, video in enumerate(videos, 1):
            print(f"Тестирование {i}/{len(videos)}: {video['title']}...")
            result = test_video_transcript(video['video_id'], video['title'])
            results.append(result)
            
            # Save progress after each test
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'channel_id': CHANNEL_ID,
                        'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'total_videos': len(videos)
                    },
                    'results': results
                }, f, ensure_ascii=False, indent=2)
            
            # Be nice to the API
            time.sleep(1)
        
        # Generate and print report
        report = generate_report(results)
        print("\n" + report)
        
        # Save report to file
        with open('rav_ginsburg_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"\nОтчёт сохранён в файл: rav_ginsburg_report.txt")
        print(f"Полные результаты тестирования сохранены в: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()
