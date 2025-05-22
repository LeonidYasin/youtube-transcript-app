from youtube_transcript_api import YouTubeTranscriptApi
import json

def test_transcript(video_id, language='ru'):
    print(f"Testing transcript for video: {video_id}, language: {language}")
    print("=" * 80)
    
    try:
        # Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        
        # Print the first 5 segments
        print("\nFirst 5 transcript segments:")
        for i, segment in enumerate(transcript[:5]):
            print(f"{i+1}. {segment}")
        
        # Print the raw text content
        print("\nRaw text content (first 500 characters):")
        text = "\n".join([s['text'] for s in transcript])
        print(text[:500] + ("..." if len(text) > 500 else ""))
        
        # Save to file to check encoding
        with open('transcript.txt', 'w', encoding='utf-8') as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)
        print("\nTranscript saved to transcript.txt")
        
        # Print encoding information
        print(f"\nText length: {len(text)} characters")
        print(f"Sample characters: {repr(text[:100])}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_transcript("qp0HIF3SfI4", "ru")
