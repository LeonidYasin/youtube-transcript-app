import requests
import json

def test_transcript_api():
    url = "http://localhost:8000/api/transcript"
    params = {
        "url": "https://www.youtube.com/watch?v=5MgBikgcWnY",
        "language": "ru"
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}..." if response.text else "No response")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_transcript_api()
