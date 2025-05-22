from youtube_transcript_api import YouTubeTranscriptApi
import json

def get_russian_transcript(video_id):
    try:
        # Get available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get Russian transcript
        try:
            # First try to find Russian transcript
            transcript = transcript_list.find_transcript(['ru'])
            print("Found Russian transcript")
        except:
            # If no Russian, try to find a translatable transcript
            for t in transcript_list:
                if t.is_translatable and 'ru' in [lang.language_code for lang in t.translation_languages]:
                    transcript = t.translate('ru')
                    print(f"Found translatable transcript in {t.language_code}, translating to Russian")
                    break
            else:
                print("No Russian transcript or translation available")
                return None
        
        # Get the transcript data
        transcript_data = transcript.fetch()
        
        # Extract text
        text = "\n".join([entry['text'] for entry in transcript_data])
        
        # Save to file with UTF-8 encoding
        with open(f'transcript_{video_id}_ru_manual.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Transcript saved to transcript_{video_id}_ru_manual.txt")
        return text
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Test with Simon Sinek's TED Talk
    video_id = "qp0HIF3SfI4"
    transcript = get_russian_transcript(video_id)
    
    if transcript:
        print("\nFirst 500 characters:")
        print("-" * 50)
        print(transcript[:500])
        print("-" * 50)
