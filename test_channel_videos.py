import requests
import json

def test_channel_videos():
    # First, get Rabbi Ginsburgh's channel ID
    print("Getting Rabbi Ginsburgh's channel ID...")
    response = requests.get("http://127.0.0.1:8000/api/channel-search/rabbi-ginsburgh")
    
    if response.status_code != 200:
        print(f"Failed to get channel ID. Status code: {response.status_code}")
        print(response.text)
        return
    
    channel_data = response.json()
    channel_id = channel_data['channel']['channel_id']
    print(f"Found channel ID: {channel_id}")
    
    # Now get the channel videos
    print("\nFetching channel videos...")
    response = requests.get(
        f"http://127.0.0.1:8000/api/channel-search/{channel_id}/videos",
        params={"max_results": 5}  # Get 5 most recent videos
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nFound {result['count']} videos:")
        for idx, video in enumerate(result['videos'], 1):
            print(f"\n{idx}. {video['title']}")
            print(f"   Published: {video['published_time']}")
            print(f"   Duration: {video['duration']}")
            print(f"   Views: {video['view_count']}")
            print(f"   URL: {video['url']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_channel_videos()
