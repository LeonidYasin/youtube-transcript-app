import requests
import sys
import io

# Set the default console encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_endpoint():
    url = "http://127.0.0.1:8000/api/channel-search/UCKadAPtEb8TTfPrQY3qwKpQ/videos?max_results=3"
    print(f"Testing URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.text)  # This will print the raw response
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoint()
