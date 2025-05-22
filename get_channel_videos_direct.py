import requests
import sys

def get_channel_videos(channel_id, max_results=5):
    """
    Get the latest videos from a YouTube channel by channel ID
    
    Args:
        channel_id: YouTube channel ID
        max_results: Maximum number of videos to return (default: 5)
    """
    # Base URL of our API
    base_url = "http://127.0.0.1:8000/api/channel-search"
    
    try:
        # Get the channel info
        print(f"Getting channel info for ID: {channel_id}")
        
        # Get the latest videos
        print(f"\nFetching {max_results} latest videos...")
        response = requests.get(
            f"{base_url}/{channel_id}/videos",
            params={"max_results": max_results}
        )
        
        if response.status_code != 200:
            print(f"Error: Failed to get videos. Status code: {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        
        if result['status'] != 'success':
            print(f"Error: {result.get('message', 'Unknown error')}")
            return
        
        # Display the videos
        print(f"\nLatest {len(result['videos'])} videos from channel {channel_id}:")
        print("-" * 80)
        
        for idx, video in enumerate(result['videos'], 1):
            print(f"{idx}. {video['title']}")
            print(f"   Published: {video['published_time']}")
            print(f"   Duration: {video['duration']}")
            print(f"   Views: {video['view_count']}")
            print(f"   URL: {video['url']}")
            print("-" * 80)
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Rabbi Ginsburgh's channel ID
    channel_id = "UCKadAPtEb8TTfPrQY3qwKpQ"
    
    # Get the number of videos from command line argument or use default (5)
    max_results = 5
    if len(sys.argv) > 1:
        try:
            max_results = int(sys.argv[1])
            if max_results < 1 or max_results > 50:
                print("Warning: max_results must be between 1 and 50. Using default value of 5.")
                max_results = 5
        except ValueError:
            print("Warning: Invalid max_results value. Using default value of 5.")
    
    get_channel_videos(channel_id, max_results)
