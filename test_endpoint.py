import requests
import json

def test_endpoint():
    video_id = "qp0HIF3SfI4"  # Example video ID
    url = f"http://localhost:8000/api/available-languages/{video_id}"
    
    try:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        
        print("Response Status Code:", response.status_code)
        print("Response Headers:", response.headers)
        print("\nResponse Content:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")

if __name__ == "__main__":
    test_endpoint()
