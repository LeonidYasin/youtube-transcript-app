import requests
import json
import sys

# Set the console output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# TED Talk video with known good transcripts
video_url = 'https://www.youtube.com/watch?v=HluANRwPyNo'  # Simon Sinek: How great leaders inspire action

# Make the request
url = f'http://localhost:8000/api/transcript?url={video_url}&language=en'
print(f"Fetching transcript for: {video_url}")

response = requests.get(url)

# Print the response with proper encoding
try:
    data = response.json()
    if data.get('success') and data.get('transcript'):
        print("\nTranscript preview (first 500 characters):")
        print("-" * 80)
        print(data['transcript'][:500] + "..." if len(data['transcript']) > 500 else data['transcript'])
        print("\nSuccessfully retrieved transcript!")
    else:
        print("\nFailed to get transcript:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {str(e)}")
    print("Raw response:")
    print(response.text)
