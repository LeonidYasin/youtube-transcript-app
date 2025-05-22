from youtube_transcript_api import YouTubeTranscriptApi

def list_available_transcripts(video_id):
    print(f"Listing available transcripts for video: {video_id}")
    print("-" * 80)
    
    try:
        # Get list of all transcripts for the video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        print(f"Found {len(list(transcript_list))} transcript(s)")
        
        # Print information about each transcript
        for transcript in transcript_list:
            print(f"Language: {transcript.language}")
            print(f"Language code: {transcript.language_code}")
            print(f"Is generated: {transcript.is_generated}")
            
            # Handle translation languages safely
            try:
                trans_langs = []
                for tl in transcript.translation_languages:
                    trans_langs.append(f"{tl.language_code} ({tl.language})")
                print(f"Translation languages: {', '.join(trans_langs) if trans_langs else 'None'}")
            except Exception as tl_error:
                print(f"Could not get translation languages: {str(tl_error)}")
            
            # Try to fetch the transcript
            try:
                transcript_data = transcript.fetch()
                if transcript_data and len(transcript_data) > 0:
                    first_segment = transcript_data[0].get('text', 'No text')
                    print(f"  First segment: {first_segment[:100]}")
                    
                    # Print encoding information
                    try:
                        raw_bytes = first_segment.encode('latin1')
                        print(f"  Raw bytes (first 20): {' '.join(f'{b:02x}' for b in raw_bytes[:20])}")
                        
                        # Try common encodings
                        for enc in ['utf-8', 'utf-16-le', 'utf-16-be', 'cp1251']:
                            try:
                                decoded = raw_bytes.decode(enc)
                                print(f"  Decoded with {enc}: {decoded[:50]}")
                            except UnicodeDecodeError:
                                print(f"  Failed to decode with {enc}")
                                
                    except Exception as enc_error:
                        print(f"  Error analyzing encoding: {str(enc_error)}")
                else:
                    print("  No content")
                    
            except Exception as e:
                error_msg = str(e)
                print(f"  Error fetching transcript: {error_msg}")
                
                # Try to get more specific error information
                if '404' in error_msg:
                    print("  This transcript might not be available anymore")
                elif 'timed out' in error_msg.lower():
                    print("  Request timed out - YouTube might be rate limiting")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        
        # Try to get more specific error information
        try:
            from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
            
            if isinstance(e, TranscriptsDisabled):
                print("Transcripts are disabled for this video")
            elif isinstance(e, NoTranscriptFound):
                print("No transcripts found for this video")
            elif isinstance(e, VideoUnavailable):
                print("Video is unavailable")
                
        except Exception as e2:
            print(f"Could not determine specific error: {str(e2)}")

if __name__ == "__main__":
    video_id = "qp0HIF3SfI4"  # The problematic video
    list_available_transcripts(video_id)
