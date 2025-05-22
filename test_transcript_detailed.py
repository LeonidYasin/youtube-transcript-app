import requests
import json
import sys

def test_transcript_api():
    # Set default encoding to UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    url = "http://localhost:8000/api/transcript"
    params = {
        "url": "https://www.youtube.com/watch?v=0f2XchA-b9A",
        "language": "ru"
    }
    
    print("Testing YouTube Transcript API")
    print("=" * 50)
    print(f"Endpoint: {url}")
    print(f"Video URL: {params['url']}")
    print(f"Language: {params['language']}")
    
    try:
        print("\nSending GET request...")
        response = requests.get(url, params=params)
        
        print("\nResponse Status Code:", response.status_code)
        print("Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        # Try to get JSON response
        try:
            json_response = response.json()
            print("\nResponse JSON:")
            print(json.dumps(json_response, indent=2, ensure_ascii=False))
        except ValueError:
            # If not JSON, print raw content
            print("\nResponse Content (not JSON):")
            print(response.text[:1000])  # Print first 1000 chars
            
        print("\nRaw response content:")
        print(response.content[:500])  # Print first 500 bytes
            
    except Exception as e:
        print("\nError:", str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transcript_api()
