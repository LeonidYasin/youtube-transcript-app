import requests
import json
import sys
from urllib.parse import urljoin

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def test_endpoint(self, method, endpoint, params=None, json_data=None):
        url = urljoin(self.base_url, endpoint)
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, params=params, json=json_data)
            else:
                return f"Unsupported method: {method}"
            
            return {
                'status_code': response.status_code,
                'response': response.text,
                'url': response.url,
                'headers': dict(response.headers)
            }
        except Exception as e:
            return {
                'error': str(e),
                'url': url,
                'params': params
            }
    
    def print_result(self, test_name, result):
        print(f"\n{'='*50}")
        print(f"TEST: {test_name}")
        print("-" * 50)
        if 'error' in result:
            print(f"ERROR: {result['error']}")
            print(f"URL: {result['url']}")
            print(f"Params: {result['params']}")
        else:
            print(f"URL: {result['url']}")
            print(f"Status Code: {result['status_code']}")
            print("Response:")
            try:
                print(json.dumps(json.loads(result['response']), indent=2, ensure_ascii=False))
            except:
                print(result['response'][:1000])
        print("="*50)

def main():
    tester = APITester()
    
    # Test 1: Get transcript with video URL and language
    print("\n" + "="*50)
    print("TESTING YOUTUBE TRANSCRIPT API")
    print("="*50)
    
    # Test different endpoints and parameters
    test_cases = [
        # Test with full YouTube URL and language
        (
            "Get transcript with full YouTube URL",
            "GET",
            "/api/transcript",
            {"url": "https://www.youtube.com/watch?v=5MgBikgcWnY", "language": "ru"}
        ),
        # Test with just video ID
        (
            "Get transcript with video ID only",
            "GET",
            "/api/transcript",
            {"url": "5MgBikgcWnY", "language": "ru"}
        ),
        # Test with different video that likely has subtitles
        (
            "Get transcript with different video",
            "GET",
            "/api/transcript",
            {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "language": "en"}
        ),
        # Test with invalid URL
        (
            "Get transcript with invalid URL",
            "GET",
            "/api/transcript",
            {"url": "invalid-url", "language": "ru"}
        ),
        # Test health check endpoint
        (
            "Health check",
            "GET",
            "/health",
            {}
        ),
        # Test root endpoint (should redirect to docs)
        (
            "Root endpoint",
            "GET",
            "/",
            {}
        )
    ]
    
    for name, method, endpoint, params in test_cases:
        result = tester.test_endpoint(method, endpoint, params)
        tester.print_result(name, result)
    
    # Test available languages endpoint if it exists
    result = tester.test_endpoint("GET", "/api/languages")
    tester.print_result("Get available languages", result)

if __name__ == "__main__":
    main()
