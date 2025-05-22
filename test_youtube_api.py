from youtube_transcript_api import YouTubeTranscriptApi

def test_video_languages(video_id):
    print(f"Testing video ID: {video_id}")
    print("-" * 50)
    
    try:
        # Try to list all available transcripts
        print("\nAvailable transcripts:")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        for transcript in transcript_list:
            print(f"\nLanguage: {transcript.language} ({transcript.language_code})")
            print(f"Is generated: {transcript.is_generated}")
            print(f"Is translatable: {transcript.is_translatable}")
            
            # Try to get the transcript
            try:
                transcript_text = transcript.fetch()
                print(f"Successfully fetched {len(transcript_text)} segments")
                if transcript_text:
                    print(f"First 100 chars: {transcript_text[0]['text'][:100]}...")
            except Exception as e:
                print(f"Error fetching transcript: {str(e)}")
            
            # List available translations
            try:
                translations = list(transcript.translation_languages)
                if translations:
                    print("\nAvailable translations:")
                    for t in translations:
                        print(f"- {t['language']} ({t['language_code']})")
            except Exception as e:
                print(f"Error getting translations: {str(e)}")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    # Test with Simon Sinek's TED Talk
    test_video_languages("qp0HIF3SfI4")
