from youtube_transcript_api import YouTubeTranscriptApi

def get_fixed_transcript(video_id, lang='ru'):
    try:
        # Get the raw transcript data
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        
        # Extract text and fix encoding
        text_segments = []
        for entry in transcript:
            raw_text = entry['text']
            try:
                # Try decoding with windows-1251 if it looks like it needs it
                if any(ord(c) > 127 for c in raw_text):
                    try:
                        fixed = raw_text.encode('latin1').decode('windows-1251')
                        text_segments.append(fixed)
                        continue
                    except UnicodeError:
                        pass
                text_segments.append(raw_text)
            except Exception as e:
                print(f"Error processing text: {str(e)}")
                text_segments.append(raw_text)
        
        # Combine all segments
        full_text = "\n".join(text_segments)
        
        # Save to file
        output_file = f'transcript_{video_id}_fixed.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        print(f"Transcript saved to {output_file}")
        return full_text
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    video_id = "qp0HIF3SfI4"  # Simon Sinek's TED Talk
    text = get_fixed_transcript(video_id, 'ru')
    
    if text:
        print("\nFirst 500 characters:")
        print("-" * 50)
        print(text[:500])
        print("-" * 50)
