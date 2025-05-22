import requests
import json

def test_channel_search():
    base_url = "http://127.0.0.1:8000/api/channel-search"
    
    # Test 1: Search for Rabbi Ginsburgh's channel directly
    print("Testing Rabbi Ginsburgh's channel search...")
    response = requests.get(f"{base_url}/rabbi-ginsburgh")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("Rabbi Ginsburgh's channel found:")
        channel = response.json()['channel']
        print(f"Title: {channel['title']}")
        print(f"URL: {channel['url']}")
        print(f"Channel ID: {channel['channel_id']}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*80 + "\n")
    
    # Test 2: General channel search
    print("Testing general channel search...")
    response = requests.get(f"{base_url}/search", params={"query": "рав ицхак гинзбург"})
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Found {result['count']} channels:")
        for idx, channel in enumerate(result['results'], 1):
            print(f"\n{idx}. {channel['title']}")
            print(f"   URL: {channel['url']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_channel_search()
