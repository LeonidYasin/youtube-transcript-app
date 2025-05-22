import requests
import json
from datetime import datetime

def run_test(test_case):
    print(f"\n{'='*50}")
    print(f"Testing: {test_case['description']}")
    print(f"URL: {test_case['url']}")
    print(f"Language: {test_case['language']}")
    
    try:
        start_time = datetime.now()
        response = requests.get(
            'http://localhost:8000/api/transcript',
            params={'url': test_case['url'], 'language': test_case['language']}
        )
        end_time = datetime.now()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {(end_time - start_time).total_seconds():.2f} seconds")
        
        # Save the response to a file
        filename = f"test_result_{test_case['description'].replace(' ', '_')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Test: {test_case['description']}\n")
            f.write(f"URL: {test_case['url']}\n")
            f.write(f"Language: {test_case['language']}\n")
            f.write(f"Status Code: {response.status_code}\n")
            f.write(f"Response Time: {(end_time - start_time).total_seconds():.2f} seconds\n")
            f.write("-"*50 + "\n")
            f.write(response.text)
        
        print(f"Response saved to: {filename}")
        
        # Print first 100 characters of the response
        if response.text:
            print("Preview:", response.text[:100] + "...")
        
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def run_comprehensive_test():
    test_cases = [
        {
            'description': 'English video with English subtitles',
            'url': 'dQw4w9WgXcQ',  # Rick Astley - Never Gonna Give You Up
            'language': 'en'
        },
        {
            'description': 'Russian video with Russian subtitles',
            'url': '7CmkwhWqUzE',  # Some Russian video
            'language': 'ru'
        },
        {
            'description': 'Video with invalid language code',
            'url': 'dQw4w9WgXcQ',
            'language': 'xx'  # Invalid language code
        },
        {
            'description': 'Non-existent video ID',
            'url': 'thisisnotavideoid123',
            'language': 'en'
        },
        {
            'description': 'Full YouTube URL',
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'language': 'en'
        },
        {
            'description': 'Short YouTube URL',
            'url': 'https://youtu.be/dQw4w9WgXcQ',
            'language': 'en'
        }
    ]
    
    print("Starting comprehensive API testing...")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total test cases: {len(test_cases)}")
    
    successful_tests = 0
    for test_case in test_cases:
        if run_test(test_case):
            successful_tests += 1
    
    print("\n" + "="*50)
    print(f"Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tests passed: {successful_tests}/{len(test_cases)}")
    print("="*50)

if __name__ == "__main__":
    run_comprehensive_test()
