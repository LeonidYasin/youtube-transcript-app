"""
Test script for checking Rav Ginzburg's videos transcripts.
"""
import sys
import requests
from datetime import datetime

# Set console to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Base URL for the FastAPI application
BASE_URL = "http://localhost:8000/api"

# Test cases with Rav Ginzburg's videos
TEST_CASES = [
    {
        "video_id": "-l_b2ImuW70",  # "Душа". "Одно напротив другого"
        "name": "Rav Ginzburg - Душа. Одно напротив другого",
        "languages": ["he", "ru"],
        "expected_language": "he"
    },
    {
        "video_id": "6KSAUbwQMrI",  # Время решать (1)
        "name": "Rav Ginzburg - Время решать (1)",
        "languages": ["he", "ru"],
        "expected_language": "he"
    },
    {
        "video_id": "LMA2o6cfVBI",  # Выбор между...
        "name": "Rav Ginzburg - Выбор между...",
        "languages": ["he", "ru"],
        "expected_language": "he"
    },
    {
        "video_id": "aIwi0katIVI",  # Смягчение судов
        "name": "Rav Ginzburg - Смягчение судов",
        "languages": ["he", "ru"],
        "expected_language": "he"
    },
    {
        "video_id": "dQw4w9WgXcQ",  # This is a test video that should be available
        "name": "Test Video (Should be available)",
        "languages": ["en"],
        "expected_language": "en"
    }
]

def print_header(text, width=80):
    """Print a formatted header."""
    print("\n" + "=" * width)
    print(f"{text:^{width}}")
    print("=" * width)

def print_success(msg):
    """Print a success message."""
    print(f"[SUCCESS] {msg}")

def print_error(msg):
    """Print an error message."""
    print(f"[ERROR] {msg}")

def print_info(msg):
    """Print an info message."""
    print(f"[INFO] {msg}")

def test_video(video_id, language, expected_language, expect_failure=False):
    """Test fetching transcript for a single video."""
    print(f"\nTesting video: {video_id} (language: {language})")
    
    try:
        response = requests.get(
            f"{BASE_URL}/transcript",
            params={"url": video_id, "language": language, "auto_generated": True}
        )
        
        if response.status_code == 200:
            if expect_failure:
                print_error("Expected failure but request succeeded")
                return False
                
            print_success(f"Found transcript in {language}")
            print(f"   Video ID: {video_id}")
            print(f"   Language: {language}")
            print(f"   Length: {len(response.text)} characters")
            return True
        else:
            if not expect_failure:
                print_error(f"API returned status {response.status_code}")
                print(f"   Error: {response.text.strip()}")
                return False
            else:
                print_success(f"Expected failure received: {response.text.strip()}")
                return True
                
    except Exception as e:
        print_error(f"Error testing video {video_id}: {str(e)}")
        return False

def main():
    """Main function to run all test cases."""
    print("=" * 80)
    print(" " * 30 + "RAV GINZBURG VIDEOS TEST" + " " * 30)
    print("=" * 80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing against server: {BASE_URL}\n")

    success_count = 0
    total_tests = 0
    
    for test_case in TEST_CASES:
        video_id = test_case["video_id"]
        video_name = test_case["name"]
        expect_failure = test_case.get("expect_failure", False)
        
        print_header(f"TESTING: {video_name}")
        print(f"Video ID: {video_id}")
        print(f"Languages to test: {', '.join(test_case['languages'])}")
        
        video_success = 0
        video_total = 0
        
        for lang in test_case["languages"]:
            total_tests += 1
            video_total += 1
            
            print(f"\n--- Testing {lang} ---")
            if test_video(video_id, lang, test_case["expected_language"], expect_failure):
                success_count += 1
                video_success += 1
        
        # Print video test result
        status = "PASSED" if video_success == video_total else "FAILED"
        print(f"\n{status}: {video_success}/{video_total} tests passed for {video_name}")
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {success_count}")
    print(f"Failed: {total_tests - success_count}")
    print(f"Success Rate: {success_count/max(1, total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print_success("All tests passed successfully!")
    else:
        print_error(f"{total_tests - success_count} test(s) failed")
    
    return success_count == total_tests

if __name__ == "__main__":
    import sys
    
    # Check if the server is running
    try:
        response = requests.get(f"{BASE_URL}", timeout=5)
        if response.status_code != 200:
            print_error("Server is not running. Please start the server first.")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print_error("Could not connect to the server. Please make sure it's running.")
        sys.exit(1)
    
    if not main():
        sys.exit(1)
