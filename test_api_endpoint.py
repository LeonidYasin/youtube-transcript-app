import requests
import json

def test_transcript():
    try:
        # Test with a popular video that likely has subtitles
        response = requests.get(
            'http://localhost:8000/api/transcript',
            params={
                'url': 'dQw4w9WgXcQ',  # Rick Astley - Never Gonna Give You Up
                'language': 'en'
            }
        )
        
        print(f"Status Code: {response.status_code}")
        
        # Try to decode as JSON first
        try:
            data = response.json()
            print("Response (JSON):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except ValueError:
            # If not JSON, print as text
            print("Response (Text):")
            print(response.text[:1000])  # Print first 1000 chars
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_transcript()
