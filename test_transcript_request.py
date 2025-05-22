import requests
import json

def test_transcript_api():
    url = "http://localhost:8000/api/transcript/"
    params = {
        "url": "https://www.youtube.com/watch?v=0f2XchA-b9A",
        "language": "ru"
    }
    
    print("Sending request to:", url)
    print("Parameters:", json.dumps(params, indent=2))
    
    try:
        response = requests.get(url, params=params)
        print("\nResponse Status Code:", response.status_code)
        print("Response Headers:", dict(response.headers))
        
        try:
            print("\nResponse JSON:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except ValueError:
            print("\nResponse Content (not JSON):")
            print(response.text)
            
    except Exception as e:
        print("\nError making request:", str(e))

if __name__ == "__main__":
    test_transcript_api()
