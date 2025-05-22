import requests
import json
import sys

def test_transcript_endpoint():
    url = "http://localhost:8000/api/transcript/"
    params = {
        "url": "https://www.youtube.com/watch?v=5MgBikgcWnY",
        "language": "en"
    }
    
    try:
        # Set up the session with proper headers
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Make the request
        response = session.get(url, params=params)
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
            
        # Try to parse JSON if possible
        try:
            print("\nResponse JSON:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except ValueError:
            print("\nResponse Content (first 500 chars):")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    # Set console output encoding to UTF-8
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    test_transcript_endpoint()
