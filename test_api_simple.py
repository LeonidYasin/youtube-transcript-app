import requests
import sys

def test_api():
    try:
        # Set console output encoding to UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        
        # Test the API endpoint
        response = requests.get(
            'http://localhost:8000/api/transcript',
            params={'url': 'dQw4w9WgXcQ', 'language': 'en'}
        )
        
        print(f'Status Code: {response.status_code}')
        print('Response:')
        
        # Try to print the response with error handling for encoding
        try:
            print(response.text[:500])  # Print first 500 characters
        except UnicodeEncodeError:
            # If there's still an encoding error, print a message
            print("Response contains characters that cannot be displayed in the console.")
            print("Saving response to file...")
            with open('api_response.txt', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("Response saved to 'api_response.txt'")
        
    except Exception as e:
        print(f'Error: {str(e)}')

if __name__ == "__main__":
    test_api()
