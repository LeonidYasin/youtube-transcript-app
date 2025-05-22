from youtube_transcript_api import YouTubeTranscriptApi
import binascii

def print_hex_dump(data, length=32):
    """Print a hex dump of the data"""
    for i in range(0, len(data), length):
        chunk = data[i:i+length]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        print(f"{i:08x}  {hex_str.ljust(length*3)}  |{ascii_str}|")

def test_video_transcript(video_id, language='ru'):
    print(f"Testing video: {video_id}, language: {language}")
    print("-" * 80)
    
    try:
        # Get the raw transcript data
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=[language],
            preserve_formatting=True
        )
        
        if not transcript:
            print("No transcript found")
            return
            
        print(f"Found {len(transcript)} transcript segments")
        
        # Print first 3 segments for analysis
        for i, segment in enumerate(transcript[:3]):
            print(f"\n--- Segment {i+1} ---")
            print(f"Original text: {segment['text']}")
            
            # Get raw bytes of the text
            try:
                # Try to encode as latin1 first (preserves raw bytes)
                raw_bytes = segment['text'].encode('latin1')
                print("Raw bytes (hex):", ' '.join(f'{b:02x}' for b in raw_bytes))
                
                # Try different encodings
                encodings = ['utf-8', 'utf-16-le', 'utf-16-be', 'cp1251', 'cp1252', 'iso-8859-1', 'koi8-r']
                
                for enc in encodings:
                    try:
                        # Try direct decode
                        decoded = raw_bytes.decode(enc)
                        print(f"{enc}: {decoded[:100]}")
                    except UnicodeDecodeError:
                        print(f"{enc}: Decode error")
                    
                    # Try double decode (common issue)
                    try:
                        double_decoded = raw_bytes.decode('latin1').encode('latin1').decode(enc)
                        if double_decoded != segment['text']:  # Only print if different
                            print(f"  (double) {enc}: {double_decoded[:100]}")
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        pass
                        
            except Exception as e:
                print(f"Error processing segment: {str(e)}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    video_id = "qp0HIF3SfI4"  # The problematic video
    test_video_transcript(video_id, 'ru')
