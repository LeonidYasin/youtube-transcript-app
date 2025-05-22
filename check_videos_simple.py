import sys
import os
import json
import io
from datetime import datetime

# Set console encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure the app directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.youtube import YouTubeService

def check_video(video_id):
    """Check if a video has Russian subtitles."""
    youtube = YouTubeService()
    result = {
        'video_id': video_id,
        'has_russian': False,
        'error': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # Try to get Russian subtitles
        transcript, _ = youtube.get_subtitles(video_id, 'ru')
        if transcript:
            result['has_russian'] = True
            result['sample'] = transcript[:200]  # First 200 chars as sample
        else:
            result['error'] = "No Russian subtitles found"
    except Exception as e:
        result['error'] = str(e)
    
    return result

def main():
    # List of video IDs to check (you can add more)
    video_ids = [
        "xXU4-tiX4Wk",  # The video we've been working with
        "dQw4w9WgXcQ",  # Example video 1
        "9bZkp7q19f0",  # Example video 2
        "KQ6zr6kCPj8",  # Example video 3
        "JGwWNGJdvx8",  # Example video 4
        "OPf0YbXqDm0",  # Example video 5
        "kOkQ4T5WO9E",  # Example video 6
        "tgbNymZ7vqY",  # Example video 7
        "2Vv-BfVoq4g",  # Example video 8
        "JGwWNGJdvx9",  # Example video 9
    ]
    
    print(f"Checking {len(video_ids)} videos for Russian subtitles...\n")
    
    results = []
    for i, video_id in enumerate(video_ids, 1):
        print(f"Checking video {i}/{len(video_ids)}: {video_id}")
        result = check_video(video_id)
        results.append(result)
        
        status = "[OK]" if result['has_russian'] else "[--]"
        error_msg = f" - {result['error']}" if result['error'] else ""
        print(f"  {status} Video {video_id}: {'Has Russian subtitles' if result['has_russian'] else 'No Russian subtitles'}{error_msg}")
    
    # Save results to file
    os.makedirs('test_results', exist_ok=True)
    output_file = 'test_results/subtitle_check.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_videos': len(results),
            'videos_with_russian': sum(1 for r in results if r['has_russian']),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
