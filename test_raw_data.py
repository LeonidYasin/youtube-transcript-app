from youtube_transcript_api import YouTubeTranscriptApi
import json
import binascii

def save_raw_transcript(video_id, language='ru'):
    print(f"Fetching transcript for video: {video_id}, language: {language}")
    
    try:
        # Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=[language],
            preserve_formatting=True
        )
        
        if not transcript:
            print("No transcript found")
            return
            
        print(f"Found {len(transcript)} segments")
        
        # Save raw data to file
        with open('raw_transcript.json', 'w', encoding='utf-8') as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)
            
        print("Raw data saved to raw_transcript.json")
        
        # Print first segment for analysis
        if transcript:
            first_segment = transcript[0]
            print("\nFirst segment:")
            print(json.dumps(first_segment, ensure_ascii=False, indent=2))
            
            # Print raw bytes of the text
            text = first_segment.get('text', '')
            print("\nRaw bytes of text:")
            print(f"Length: {len(text)} characters")
            print(f"First 100 chars: {text[:100]}")
            
            # Print hex representation
            try:
                raw_bytes = text.encode('latin1')  # Preserve raw bytes
                print("\nHex dump of first 100 bytes:")
                hex_dump = ' '.join(f'{b:02x}' for b in raw_bytes[:100])
                print(hex_dump)
                
                # Try to detect encoding
                print("\nTrying different encodings:")
                for enc in ['utf-8', 'utf-16-le', 'utf-16-be', 'cp1251', 'cp1252']:
                    try:
                        decoded = raw_bytes.decode(enc)
                        print(f"{enc}: {decoded[:100]}")
                    except UnicodeDecodeError as e:
                        print(f"{enc}: Error - {str(e)}")
                        
            except Exception as e:
                print(f"Error processing bytes: {str(e)}")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        
        # Try to get more detailed error information
        try:
            from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, TooManyRequests, TranscriptsDisabled, NoTranscriptFound
            
            if isinstance(e, TranscriptsDisabled):
                print("Transcripts are disabled for this video")
            elif isinstance(e, NoTranscriptFound):
                print("No transcript found for the specified language")
            elif isinstance(e, VideoUnavailable):
                print("Video is unavailable")
            elif isinstance(e, TooManyRequests):
                print("Too many requests to YouTube")
                
        except Exception as e2:
            print(f"Could not determine specific error: {str(e2)}")

if __name__ == "__main__":
    video_id = "qp0HIF3SfI4"  # The problematic video
    save_raw_transcript(video_id, 'ru')
