from youtube_transcript_api import YouTubeTranscriptApi
import json
import sys

def print_utf8(*args, **kwargs):
    """Helper function to print UTF-8 encoded text"""
    text = ' '.join(str(arg) for arg in args)
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        # If we can't print to console, write to a file
        with open('transcript_output.txt', 'w', encoding='utf-8') as f:
            f.write(text + '\n')
        print("Output written to transcript_output.txt", **kwargs)

def test_video(video_id, language='ru'):
    print_utf8(f"Testing video: {video_id}, language: {language}")
    print_utf8("-" * 80)
    
    try:
        # Try to get the transcript directly
        print_utf8(f"Attempting to fetch transcript for language: {language}")
        
        # Get the raw transcript data
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=[language],
            preserve_formatting=True
        )
        
        if not transcript:
            print_utf8("No transcript found")
            return
            
        print_utf8(f"Successfully retrieved {len(transcript)} segments")
        
        # Save raw data to file
        with open('raw_transcript.json', 'w', encoding='utf-8') as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)
        print_utf8("Raw transcript data saved to raw_transcript.json")
        
        # Print first few segments with encoding information
        print_utf8("\nFirst 3 segments:")
        for i, segment in enumerate(transcript[:3]):
            print_utf8(f"\nSegment {i+1}:")
            
            # Print the raw dictionary
            print_utf8("Raw segment data:")
            for key, value in segment.items():
                print_utf8(f"  {key}: {value}")
            
            # Print text with encoding info
            if 'text' in segment:
                text = segment['text']
                print_utf8("\nText content:")
                print_utf8(f"  Length: {len(text)} characters")
                print_utf8(f"  First 100 chars: {text[:100]}")
                
                # Try to detect encoding
                try:
                    # Try to encode as latin1 to preserve raw bytes
                    raw_bytes = text.encode('latin1')
                    print_utf8("\nRaw bytes (first 20):")
                    hex_dump = ' '.join(f'{b:02x}' for b in raw_bytes[:20])
                    print_utf8(f"  {hex_dump}")
                    
                    # Try common encodings
                    print_utf8("\nAttempting different decodings:")
                    for enc in ['utf-8', 'utf-16-le', 'utf-16-be', 'cp1251', 'cp1252', 'iso-8859-1']:
                        try:
                            decoded = raw_bytes.decode(enc)
                            print_utf8(f"  {enc}: {decoded[:50]}")
                        except UnicodeDecodeError:
                            print_utf8(f"  {enc}: Decode error")
                            
                    # Try double decoding (common issue with some APIs)
                    try:
                        double_decoded = raw_bytes.decode('latin1').encode('latin1').decode('cp1251')
                        print_utf8(f"\nDouble decoded (latin1->latin1->cp1251): {double_decoded[:50]}")
                    except Exception as e:
                        print_utf8(f"  Double decode error: {str(e)}")
                        
                except Exception as e:
                    print_utf8(f"Error analyzing text: {str(e)}")
            
            print_utf8("-" * 40)
        
    except Exception as e:
        print_utf8(f"Error: {str(e)}")
        
        # Print the full exception with traceback
        import traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print_utf8("\nFull traceback:")
        print_utf8(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))

if __name__ == "__main__":
    video_id = "qp0HIF3SfI4"  # The problematic video
    test_video(video_id, 'ru')
