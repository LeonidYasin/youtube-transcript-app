import requests
import json

def test_transcript_endpoint():
    url = "http://localhost:8000/transcript/"
    params = {
        "url": "https://www.youtube.com/watch?v=5MgBikgcWnY",
        "language": "en"
    }
    headers = {
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response Headers:", response.headers)
        
        # Try to parse JSON
        try:
            print("\nResponse JSON:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except ValueError:
            print("\nResponse Content (first 500 chars):")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_transcript_endpoint()
