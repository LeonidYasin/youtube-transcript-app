import requests
import json

def test_available_languages():
    video_id = "qp0HIF3SfI4"  # Example video ID
    url = f"http://localhost:8000/api/available-languages/{video_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print("API Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get('success') and 'languages' in data:
            print("\nAvailable Languages:")
            print("-" * 80)
            for lang in data['languages']:
                print(f"{lang['code']}: {lang['name']}")
            print("-" * 80)
            
            # Check for duplicates
            codes = [lang['code'] for lang in data['languages']]
            if len(codes) != len(set(codes)):
                print("\nWARNING: Duplicate language codes found!")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_available_languages()
