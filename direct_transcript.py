from youtube_transcript_api import YouTubeTranscriptApi
import json

def get_transcript(video_id, language='ru'):
    try:
        # Get available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get the transcript in the requested language
        try:
            transcript = transcript_list.find_transcript([language])
            print(f"Found {language} transcript")
        except:
            # If not found, try to find a translatable transcript
            for t in transcript_list:
                if t.is_translatable:
                    print(f"Found translatable transcript in {t.language_code}")
                    transcript = t.translate(language)
                    break
            else:
                print(f"No {language} transcript or translation available")
                print("Available languages:")
                for t in transcript_list:
                    print(f"- {t.language_code}: {t.language}", 
                          "(auto-generated)" if t.is_generated else "")
                return None
        
        # Fetch the transcript data
        transcript_data = transcript.fetch()
        
        # Extract text
        text = "\n".join([entry['text'] for entry in transcript_data])
        
        # Save to file
        output_file = f'transcript_{video_id}_{language}.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Transcript saved to {output_file}")
        return text
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Test with a video that has Russian subtitles
    video_id = "qp0HIF3SfI4"  # Simon Sinek's TED Talk
    text = get_transcript(video_id, 'ru')
    
    if text:
        print("\nFirst 500 characters:")
        print("-" * 50)
        print(text[:500])
        print("-" * 50)
