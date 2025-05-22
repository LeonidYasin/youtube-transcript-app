from pytube import YouTube
import os

def download_captions(video_url, language_code='ru'):
    try:
        # Create a YouTube object
        yt = YouTube(video_url)
        
        print(f"Title: {yt.title}")
        print(f"Length: {yt.length} seconds")
        
        # Get available caption tracks
        caption_tracks = yt.captions
        print("\nAvailable caption tracks:")
        for lang_code in caption_tracks:
            print(f"- {lang_code}: {caption_tracks[lang_code]}")
        
        # Try to get the specified language caption
        if language_code in caption_tracks:
            print(f"\nFound {language_code} captions!")
            caption = caption_tracks[language_code]
            
            # Get the caption as XML
            xml_captions = caption.xml_captions
            
            # Save the XML to a file
            with open(f'captions_{language_code}.xml', 'w', encoding='utf-8') as f:
                f.write(xml_captions)
            print(f"Saved XML captions to captions_{language_code}.xml")
            
            # Convert to SRT format
            srt_captions = caption.generate_srt_captions()
            with open(f'captions_{language_code}.srt', 'w', encoding='utf-8') as f:
                f.write(srt_captions)
            print(f"Saved SRT captions to captions_{language_code}.srt")
            
            # Extract just the text
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(xml_captions, 'html.parser')
            text_captions = '\n'.join([p.text for p in soup.find_all('text')])
            
            with open(f'captions_{language_code}.txt', 'w', encoding='utf-8') as f:
                f.write(text_captions)
            print(f"Saved text captions to captions_{language_code}.txt")
            
            print("\nPreview of the captions:")
            print('\n'.join([p.text for p in soup.find_all('text')][:5]))
            
            return text_captions
        else:
            print(f"\nNo {language_code} captions found.")
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
    language_code = 'ru'
    
    print(f"Attempting to download {language_code} captions for: {video_url}")
    captions = download_captions(video_url, language_code)
