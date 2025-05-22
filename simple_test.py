import requests
import json

def test_api():
    try:
        # Test the API endpoint
        response = requests.get(
            'http://localhost:8000/api/transcript',
            params={'url': 'dQw4w9WgXcQ', 'language': 'en'}
        )
        
        # Save the response to a file with UTF-8 encoding
        with open('api_response.txt', 'w', encoding='utf-8') as f:
            f.write(f'Status Code: {response.status_code}\n')
            f.write('Response:\n')
            f.write(response.text)
            
        print(f'Status Code: {response.status_code}')
        print('Response saved to api_response.txt')
        
    except Exception as e:
        print(f'Error: {str(e)}')

if __name__ == "__main__":
    test_api()
