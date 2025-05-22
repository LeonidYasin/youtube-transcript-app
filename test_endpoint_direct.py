import sys
import os
import requests

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Test the endpoint directly
url = "http://127.0.0.1:8000/api/channel-search/UCKadAPtEb8TTfPrQY3qwKpQ/videos?max_results=3"
print(f"Testing URL: {url}")

try:
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response content: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Try a different approach with a session
print("\nTrying with a session:")
try:
    with requests.Session() as session:
        response = session.get(url)
        print(f"Status code: {response.status_code}")
        print(f"Response content: {response.text}")
except Exception as e:
    print(f"Error with session: {e}")
