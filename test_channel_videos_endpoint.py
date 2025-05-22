import requests
import json

def test_channel_videos_endpoint():
    base_url = "http://127.0.0.1:8000/api/channel-search"
    channel_id = "UCKadAPtEb8TTfPrQY3qwKpQ"
    max_results = 3
    
    print(f"Testing channel videos endpoint for channel ID: {channel_id}")
    print(f"URL: {base_url}/{channel_id}/videos?max_results={max_results}")
    
    try:
        response = requests.get(
            f"{base_url}/{channel_id}/videos",
            params={"max_results": max_results}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print("Response Headers:", response.headers)
        
        try:
            json_response = response.json()
            print("\nResponse JSON:")
            print(json.dumps(json_response, indent=2, ensure_ascii=False))
        except ValueError:
            print("\nResponse is not JSON:")
            print(response.text)
    
    except Exception as e:
        print(f"\nError making request: {e}")

if __name__ == "__main__":
    test_channel_videos_endpoint()
