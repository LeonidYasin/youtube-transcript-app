import requests

def test_transcript_api():
    url = "http://localhost:8000/api/transcript"
    params = {
        "url": "https://www.youtube.com/watch?v=5MgBikgcWnY",
        "language": "ru"
    }
    headers = {
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response Headers:", response.headers)
        print("Response Content:", response.text[:1000])  # Print first 1000 chars
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_transcript_api()
