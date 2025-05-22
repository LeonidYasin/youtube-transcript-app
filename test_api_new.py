import requests
import json

def test_api():
    url = "http://localhost:8000/api/transcript"
    params = {
        "url": "https://www.youtube.com/watch?v=qp0HIF3SfI4",
        "language": "ru"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print("API Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get('success'):
            print("\nTranscript preview:")
            print("-" * 80)
            print(data.get('transcript', 'No transcript found')[:500] + "..." if data.get('transcript') else 'No transcript content')
            print("-" * 80)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
