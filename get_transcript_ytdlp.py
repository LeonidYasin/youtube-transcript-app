"""
Script to download YouTube transcript using yt-dlp.
"""
import sys
import json
import yt_dlp

def download_transcript(video_id, language='iw'):
    """Download transcript for a YouTube video using yt-dlp."""
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [language],
        'quiet': False,
        'no_warnings': False,
        'outtmpl': f'transcript_{video_id}_%(id)s.%(ext)s',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First get the video info to check available subtitles
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
            
            # Check if automatic captions are available for the requested language
            auto_captions = info.get('automatic_captions', {})
            if language not in auto_captions:
                return False, f"No automatic captions available in language: {language}"
            
            print(f"Found automatic captions for language: {language}")
            
            # Now download the subtitles
            result = ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
            
            # The subtitles should be saved to a file by yt-dlp
            return True, f"Transcript downloaded successfully for video {video_id}"
            
    except Exception as e:
        return False, f"Error downloading transcript: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python get_transcript_ytdlp.py <video_id> [language]")
        print("Example: python get_transcript_ytdlp.py xXU4-tiX4Wk iw")
        return
    
    video_id = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'iw'
    
    print(f"Downloading transcript for video: {video_id} (language: {language})")
    
    success, message = download_transcript(video_id, language)
    print(message)
    
    if success:
        print(f"Check for files named 'transcript_{video_id}_*.vtt' in the current directory.")

if __name__ == "__main__":
    main()
