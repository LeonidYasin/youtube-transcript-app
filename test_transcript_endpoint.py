import requests

def test_transcript_endpoint():
    url = "http://localhost:8000/api/transcript/"
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
        print("\nResponse Content:")
        print(response.text)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_transcript_endpoint()
