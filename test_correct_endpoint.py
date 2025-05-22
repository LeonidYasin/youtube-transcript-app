import requests

def test_endpoint():
    # Base URL of our API
    base_url = "http://127.0.0.1:8000"
    
    # Channel ID for Rabbi Ginsburgh's channel
    channel_id = "UCKadAPtEb8TTfPrQY3qwKpQ"
    
    # Test the endpoint with the correct path
    endpoint = f"{base_url}/api/channel-search/{channel_id}/videos"
    print(f"Testing endpoint: {endpoint}")
    
    try:
        response = requests.get(endpoint, params={"max_results": 3})
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Found {len(result.get('videos', []))} videos:")
            for idx, video in enumerate(result.get('videos', [])[:3], 1):
                print(f"{idx}. {video.get('title')} - {video.get('published_time')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_endpoint()
