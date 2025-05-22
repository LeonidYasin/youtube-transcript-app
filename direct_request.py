import requests
import json
from urllib.parse import urlencode

def log_message(message, log_file='output.log'):
    """Helper function to log messages to a file"""
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def get_video_info(video_id):
    """Get video info including available transcripts"""
    # Clear the log file
    open('output.log', 'w', encoding='utf-8').close()
    
    log_message(f"Fetching info for video: {video_id}")
    
    # This is the endpoint that YouTube uses to get video info
    url = f"https://www.youtube.com/watch?v={video_id}&hl=en&gl=US&has_verified=1&bpctr=9999999999"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        log_message(f"Making request to: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save the raw response for inspection
        with open('youtube_response.html', 'w', encoding='utf-8', errors='replace') as f:
            f.write(response.text)
        log_message("Saved raw response to youtube_response.html")
        
        # Try to extract the ytInitialPlayerResponse JSON
        import re
        match = re.search(r'var ytInitialPlayerResponse\s*=\s*({.+?});', response.text, re.DOTALL)
        if match:
            json_str = match.group(1)
            with open('player_response.json', 'w', encoding='utf-8', errors='replace') as f:
                f.write(json_str)
            log_message("Saved player response to player_response.json")
            
            # Parse the JSON
            data = json.loads(json_str)
            
            # Extract captions info if available
            captions = data.get('captions', {})
            if captions:
                log_message("\nCaptions info found:")
                with open('captions_info.json', 'w', encoding='utf-8', errors='replace') as f:
                    json.dump(captions, f, indent=2, ensure_ascii=False)
                log_message("Saved captions info to captions_info.json")
                
                # Try to extract available languages
                try:
                    player_captions_tracklist_renderer = captions.get('playerCaptionsTracklistRenderer', {})
                    caption_tracks = player_captions_tracklist_renderer.get('captionTracks', [])
                    
                    log_message("\nAvailable caption tracks:")
                    for i, track in enumerate(caption_tracks, 1):
                        lang_code = track.get('languageCode', 'unknown')
                        lang_name = track.get('name', {}).get('simpleText', 'Unknown')
                        is_translatable = track.get('isTranslatable', False)
                        base_url = track.get('baseUrl', '')
                        
                        log_message(f"{i}. {lang_name} ({lang_code}) - Translatable: {is_translatable}")
                        log_message(f"   URL: {base_url}")
                        
                except Exception as e:
                    log_message(f"Error extracting caption tracks: {str(e)}")
            else:
                log_message("\nNo captions found in player response")
        else:
            log_message("Could not find ytInitialPlayerResponse in the HTML")
        
        # Also try to find the ytInitialData JSON
        match = re.search(r'var ytInitialData\s*=\s*({.+?});', response.text, re.DOTALL)
        if match:
            json_str = match.group(1)
            with open('initial_data.json', 'w', encoding='utf-8', errors='replace') as f:
                f.write(json_str)
            log_message("\nSaved initial data to initial_data.json")
            
            # Try to extract captions from initial data
            try:
                initial_data = json.loads(json_str)
                # Look for captions in the initial data structure
                # This path might need adjustment based on YouTube's actual structure
                caption_tracks = initial_data.get('captions', {}) \
                    .get('playerCaptionsTracklistRenderer', {}) \
                    .get('captionTracks', [])
                
                if caption_tracks:
                    log_message("\nFound caption tracks in initial data:")
                    with open('initial_captions.json', 'w', encoding='utf-8', errors='replace') as f:
                        json.dump(caption_tracks, f, indent=2, ensure_ascii=False)
                    log_message("Saved initial captions to initial_captions.json")
                    
            except Exception as e:
                log_message(f"Error processing initial data: {str(e)}")
        
        log_message("\nProcessing complete. Check the generated files for details.")
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        log_message(error_msg)
        import traceback
        log_message("\nTraceback:")
        log_message(traceback.format_exc())
        
        # Also save the response text if available
        if 'response' in locals():
            try:
                with open('error_response.html', 'w', encoding='utf-8', errors='replace') as f:
                    f.write(response.text)
                log_message("Saved error response to error_response.html")
            except Exception as save_error:
                log_message(f"Failed to save error response: {str(save_error)}")

def main():
    video_id = "qp0HIF3SfI4"  # The problematic video
    print(f"Fetching info for video: {video_id}")
    get_video_info(video_id)

if __name__ == "__main__":
    main()
