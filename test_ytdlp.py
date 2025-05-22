"""
Test script to check available transcripts using yt-dlp.
"""
import sys
import json
import yt_dlp

def list_transcripts(video_id):
    """List all available transcripts for a video."""
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'allsubtitles': True,
        'writeautomaticsub': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
            return info
        except Exception as e:
            return {'error': str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_ytdlp.py <video_id>")
        return
        
    video_id = sys.argv[1]
    print(f"Checking available transcripts for video: {video_id}")
    
    result = list_transcripts(video_id)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    # Save the full info to a file
    with open(f'video_info_{video_id}.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Video info saved to video_info_{video_id}.json")
    
    # Print available subtitles
    if 'subtitles' in result or 'automatic_captions' in result:
        print("\nAvailable subtitles:")
        if 'subtitles' in result:
            print("\nManual subtitles:")
            for lang, subs in result['subtitles'].items():
                print(f"- {lang}: {len(subs)} format(s)")
        
        if 'automatic_captions' in result:
            print("\nAutomatic captions:")
            for lang, subs in result['automatic_captions'].items():
                print(f"- {lang}: {len(subs)} format(s)")
    else:
        print("No subtitles available for this video.")

if __name__ == "__main__":
    main()
