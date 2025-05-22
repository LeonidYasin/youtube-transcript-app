from youtube_transcript_api import YouTubeTranscriptApi
import json

def test_transcript_encoding(video_id, language='ru'):
    print(f"Testing transcript encoding for video: {video_id}, language: {language}")
    print("=" * 80)
    
    try:
        # Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        
        # Print the first few segments
        print("\nFirst 5 transcript segments:")
        for i, segment in enumerate(transcript[:5]):
            print(f"{i+1}. {segment}")
        
        # Print the raw text content
        print("\nRaw text content:")
        text = "\n".join([s['text'] for s in transcript])
        print(text[:500] + "..." if len(text) > 500 else text)
        
        # Check for non-ASCII characters
        non_ascii = [c for c in text if ord(c) > 127]
        print(f"\nNon-ASCII characters found: {len(non_ascii)}")
        if non_ascii:
            print(f"Sample non-ASCII characters: {non_ascii[:20]}")
        
        # Try different encodings
        print("\nTrying different encodings:")
        encodings = ['utf-8', 'cp1251', 'cp1252', 'iso-8859-1', 'koi8-r']
        for enc in encodings:
            try:
                encoded = text.encode(enc)
                print(f"- {enc}: Success (length: {len(encoded)})")
            except Exception as e:
                print(f"- {enc}: Failed - {str(e)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Test with Simon Sinek's TED Talk
    test_transcript_encoding("qp0HIF3SfI4", "ru")
