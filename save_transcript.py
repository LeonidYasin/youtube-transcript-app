from app.services.youtube import YouTubeService

def save_transcript(video_id, lang='iw', filename='transcript.txt'):
    """Save transcript to a file."""
    service = YouTubeService()
    text, error = service.get_subtitles(video_id, lang)
    
    if text:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Transcript saved to {filename}")
        return True
    else:
        print(f"Error: {error}")
        return False

if __name__ == "__main__":
    video_id = "xXU4-tiX4Wk"  # Rav Ginzburg video
    save_transcript(video_id)
