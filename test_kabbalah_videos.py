"""
Test script for Kabbalah video transcripts using the FastAPI application.
"""
import sys
import json
import requests
from datetime import datetime

# Set console to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Base URL for the FastAPI application
BASE_URL = "http://localhost:8000/api"

# Test cases with various videos to test different scenarios
TEST_CASES = [
    # Videos that should work
    {
        "video_id": "k85mRPqvMbE",  # Video with auto-generated subtitles
        "name": "Sample Video with Subtitles",
        "languages": ["en"],
        "expected_language": "en",
        "expect_failure": False
    },
    {
        "video_id": "dQw4w9WgXcQ",  # Well-known video with manual subtitles
        "name": "Test Video (Always Available)",
        "languages": ["en"],
        "expected_language": "en",
        "expect_failure": False
    },
    {
        "video_id": "jNQXAC9IVRw",  # First YouTube video with good subtitle support
        "name": "Test Video 2 (High Availability)",
        "languages": ["en"],
        "expected_language": "en",
        "expect_failure": False
    },
    # Videos that are no longer available
    {
        "video_id": "9dBk2VQ8aXQ",
        "name": "Unavailable Video 1 (Should fail with proper message)",
        "languages": ["en"],
        "expected_language": "en",
        "expect_failure": True
    },
    {
        "video_id": "X0zud1Qac2o",
        "name": "Unavailable Video 2 (Should fail with proper message)",
        "languages": ["en"],
        "expected_language": "en",
        "expect_failure": True
    },
    # Kabbalah-related videos (this video is no longer available)
    {
        "video_id": "7ZqJlAE-4W4",
        "name": "Kabbalah in Hebrew (Video no longer available)",
        "languages": ["he", "en"],
        "expected_language": "he",
        "expect_failure": True  # Expecting failure because video is removed
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

def print_warning(msg):
    """Print a warning message."""
    print(f"[WARNING] {msg}")

def print_info(msg):
    """Print an info message."""
    print(f"[INFO] {msg}")

def test_video(video_id, language, expected_language, expect_failure=False):
    """Test fetching transcript for a single video."""
    print(f"\nTesting video: {video_id} (language: {language})")
    
    def try_get_transcript(use_auto_generated):
        """Helper function to try getting transcript with given settings."""
        try:
            print_info(f"Trying with auto_generated={use_auto_generated}...")
            response = requests.get(
                f"{BASE_URL}/transcript",
                params={
                    "url": video_id,
                    "language": language,
                    "auto_generated": use_auto_generated
                },
                timeout=10
            )
            return response, None
        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {str(e)}"
    
    try:
        # First try with auto_generated=True
        response, error = try_get_transcript(use_auto_generated=True)
        
        # If that fails with 404, try with auto_generated=False
        if response is None or response.status_code == 404:
            if error:
                print_warning(f"First attempt failed: {error}")
            print_info("Trying with auto_generated=False...")
            response, error = try_get_transcript(use_auto_generated=False)
        
        # If we still don't have a response, raise an error
        if response is None:
            print_error(f"All attempts failed. Last error: {error}")
            return False
            
        # Check if the request was successful
        if response.status_code == 200:
            # For text response
            transcript_text = response.text.strip()
            is_auto_generated = response.headers.get('x-transcript-source') == 'auto-generated'
            
            # Count lines in the transcript
            line_count = len([line for line in transcript_text.split('\n') if line.strip()])
            
            print_success(f"Found transcript with {line_count} lines")
            print(f"   Video ID:       {video_id}")
            print(f"   Language:       {language}")
            print(f"   Auto-generated: {is_auto_generated}")
            
            # Print a sample of the transcript
            if transcript_text:
                sample = '\n'.join(transcript_text.split('\n')[:5])  # First 5 lines
                print("\nSample transcript (first 5 lines):")
                print("   " + "\n   ".join(sample.split('\n')))
            
            # If we expected a failure but got success, that's actually a failure for this test case
            if expect_failure:
                print_error("Expected failure but request succeeded")
                return False
            return True
        else:
            error_msg = response.text.strip()
            # If we expected a failure and got one, that's a success for this test case
            if expect_failure:
                print_success(f"Expected failure received: {error_msg}")
                return True
                
            print_error(f"API returned status {response.status_code}")
            print(f"   Error: {error_msg}")
            return False
            
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False

def main():
    """Main function to run all test cases."""
    print("=" * 80)
    print(" " * 30 + "KABBALAH VIDEO TRANSCRIPT TESTER" + " " * 30)
    print("=" * 80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing against server: {BASE_URL}\n")

    success_count = 0
    total_tests = 0
    test_results = []
    
    for test_case in TEST_CASES:  # Changed from TEST_VIDEOS to TEST_CASES
        video_id = test_case["video_id"]
        video_name = test_case["name"]
        expect_failure = test_case.get("expect_failure", False)
        
        print_header(f"TESTING: {video_name}")
        print(f"Video ID: {video_id}")
        print(f"Languages to test: {', '.join(test_case['languages'])}")
        
        video_success = 0
        video_total = 0
        
        # Test each language for the video
        for lang in test_case["languages"]:
            total_tests += 1
            video_total += 1
            
            print(f"\n--- Testing {lang} ---")
            if test_video(video_id, lang, test_case["expected_language"], expect_failure):
                success_count += 1
                video_success += 1
        
        # Record video test results
        video_result = {
            'name': video_name,
            'id': video_id,
            'success': video_success,
            'total': video_total,
            'passed': video_success == video_total
        }
        test_results.append(video_result)
    
    # Print summary
    print_header("TEST SUMMARY")
    
    # Individual test results
    print("\nTest Results by Video:")
    for result in test_results:
        status = "PASSED" if result['passed'] else "FAILED"
        print(f"- {result['name']} ({result['id']}): {result['success']}/{result['total']} - {status}")
    
    # Overall statistics
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {success_count}")
    print(f"Failed: {total_tests - success_count}")
    print(f"Success Rate: {success_count/max(1, total_tests)*100:.1f}%")
    
    # Final status
    if success_count == total_tests:
        print_success("All tests passed successfully!")
    else:
        print_error(f"{total_tests - success_count} test(s) failed")
    
    return success_count == total_tests

if __name__ == "__main__":
    import sys
    
    # Check if the server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Error: FastAPI server is not running or not accessible")
            print("Please start the server using: uvicorn app.main:app --reload")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the FastAPI server")
        print("Please start the server using: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Run the tests
    if main():
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
