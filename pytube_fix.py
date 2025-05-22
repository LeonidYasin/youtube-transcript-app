from pytube import YouTube
import re
import json

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*$',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_subtitles_with_encoding_fix(video_url, lang='ru'):
    try:
        # Create YouTube object
        yt = YouTube(video_url)
        video_id = get_video_id(video_url)
        
        if not video_id:
            print("Could not extract video ID from URL")
            return None
            
        print(f"Processing video: {yt.title}")
        
        # Get captions
        caption = yt.captions.get_by_language_code(lang)
        
        if not caption:
            print(f"No {lang} captions found. Available captions:")
            for c in yt.captions:
                print(f"- {c.code}: {c.name}")
            return None
            
        # Get raw caption data
        caption_data = caption.xml_captions
        
        # Extract text from XML
        text_segments = re.findall(r'<text[^>]*>([^<]+)</text>', caption_data)
        
        # Fix encoding
        fixed_text = []
        for segment in text_segments:
            try:
                # Try windows-1251 encoding
                fixed = segment.encode('latin1').decode('windows-1251')
                fixed_text.append(fixed)
            except UnicodeError:
                fixed_text.append(segment)
        
        # Combine all segments
        full_text = '\n'.join(fixed_text)
        
        # Save to file
        output_file = f'subtitles_{video_id}_{lang}.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
            
        print(f"Subtitles saved to {output_file}")
        return full_text
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Test with Simon Sinek's TED Talk
    video_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
    text = get_subtitles_with_encoding_fix(video_url, 'ru')
    
    if text:
        print("\nFirst 500 characters:")
        print("-" * 50)
        print(text[:500])
        print("-" * 50)
