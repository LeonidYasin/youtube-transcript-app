from youtube_transcript_api import YouTubeTranscriptApi
import json

def test_transcript_encoding(video_id, language='ru'):
    print(f"Testing transcript for video: {video_id}, language: {language}")
    print("=" * 80)
    
    try:
        # Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        
        # Print basic info
        print(f"\nTranscript contains {len(transcript)} segments")
        
        # Print first 5 segments
        print("\nFirst 5 segments:")
        for i, segment in enumerate(transcript[:5]):
            print(f"{i+1}. {segment}")
        
        # Extract text from segments
        text_segments = [s['text'] for s in transcript]
        full_text = "\n".join(text_segments)
        
        # Save raw segments to JSON
        with open('transcript_raw.json', 'w', encoding='utf-8') as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)
        print("\nSaved raw transcript to transcript_raw.json")
        
        # Save text to file
        with open('transcript_text.txt', 'w', encoding='utf-8') as f:
            f.write(full_text)
        print("Saved text transcript to transcript_text.txt")
        
        # Print text stats
        print(f"\nText length: {len(full_text)} characters")
        print(f"Sample text: {repr(full_text[:200])}")
        
        # Try to detect language
        non_ascii = [c for c in full_text if ord(c) > 127]
        print(f"\nNon-ASCII characters: {len(non_ascii)}")
        if non_ascii:
            print(f"Sample non-ASCII: {non_ascii[:20]}")
        
        # Try to fix encoding issues
        print("\nTrying to fix encoding...")
        try:
            # Try to encode as cp1251 (Cyrillic Windows)
            encoded = full_text.encode('cp1251')
            decoded = encoded.decode('cp1251')
            print("Successfully encoded/decoded with cp1251")
            print(f"Sample: {decoded[:200]}")
            
            # Save fixed version
            with open('transcript_fixed.txt', 'w', encoding='utf-8') as f:
                f.write(decoded)
            print("Saved fixed transcript to transcript_fixed.txt")
            
        except Exception as e:
            print(f"Could not fix encoding: {str(e)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_transcript_encoding("qp0HIF3SfI4", "ru")
