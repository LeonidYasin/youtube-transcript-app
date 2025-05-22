import requests
import json
import sys

# Set the console output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Make the request
url = 'http://localhost:8000/api/transcript?url=https://www.youtube.com/watch?v=H14bBuluwB8&language=ru'
response = requests.get(url)

# Print the response with proper encoding
try:
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {str(e)}")
    print("Raw response:")
    print(response.text)
