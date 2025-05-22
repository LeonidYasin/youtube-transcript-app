import os
import json
import time
from datetime import datetime

# Ensure the app directory is in the Python path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)

def test_video(video_id):
    """Test the application with a single video."""
    result = {
        'video_id': video_id,
        'status': 'pending',
        'start_time': datetime.now().isoformat(),
        'end_time': None,
        'response': {'status_code': None, 'headers': {}, 'data': {}},
        'error': None,
        'transcript': None,
        'transcript_length': 0,
        'language_used': None
    }
    
    try:
        # Test the API endpoint with the correct path and parameters
        response = client.get(
            "/api/transcript",
            params={
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "language": "ru"
            },
            headers={"Accept": "application/json"}  # Explicitly request JSON
        )
        
        result['end_time'] = datetime.now().isoformat()
        
        try:
            # Get the content type from response
            content_type = response.headers.get('content-type', '').lower()
            
            if 'json' in content_type:
                # Handle JSON response
                response_data = response.json()
                result['response'] = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'data': response_data
                }
                
                if response.status_code == 200 and response_data.get('success', False):
                    result['transcript'] = response_data.get('transcript', '')
                    result['transcript_length'] = len(result['transcript'])
                    result['language_used'] = response_data.get('language_used', 'unknown')
                    result['status'] = 'success'
                else:
                    result['status'] = 'error'
                    result['error'] = response_data.get('error', 'Unknown error')
            else:
                # Handle plain text/WebVTT response
                raw_response = response.text
                result['response'] = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'content_type': content_type
                }
                
                if response.status_code == 200 and raw_response.strip():
                    result['transcript'] = raw_response
                    result['transcript_length'] = len(raw_response)
                    result['language_used'] = 'ru'  # Assuming Russian as requested
                    result['status'] = 'success'
                else:
                    result['status'] = 'error'
                    result['error'] = f"Unexpected response format: {content_type}"
                    if not raw_response.strip():
                        result['error'] = "Empty response"
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f"Unexpected error: {str(e)}"
            result['raw_response'] = response.text
                
    except Exception as e:
        result['status'] = 'exception'
        result['error'] = str(e)
        result['end_time'] = datetime.now().isoformat()
    
    return result

def main():
    # Videos with Russian subtitles from our previous check
    video_ids = [
        "xXU4-tiX4Wk",  # Has Russian subtitles
        "9bZkp7q19f0",  # Has Russian subtitles
        "tgbNymZ7vqY"   # Has Russian subtitles
    ]
    
    print(f"Testing application with {len(video_ids)} videos that have Russian subtitles...\n")
    
    # Create results directory if it doesn't exist
    os.makedirs('test_results', exist_ok=True)
    
    results = []
    
    for i, video_id in enumerate(video_ids, 1):
        print(f"Testing video {i}/{len(video_ids)}: {video_id}")
        result = test_video(video_id)
        results.append(result)
        
        status = "[OK]" if result.get('status') == 'success' else "[--]"
        print(f"  {status} Status: {result.get('status', 'unknown')}")
        
        # Safely access response data
        response_status = result.get('response', {}).get('status_code')
        if response_status is not None:
            print(f"  HTTP {response_status}")
            
        # Show error if present
        error_msg = result.get('error')
        if error_msg:
            print(f"  Error: {error_msg}")
            
        # Show transcript info if available
        transcript_len = result.get('transcript_length')
        if transcript_len is not None:
            print(f"  Transcript length: {transcript_len} characters")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'test_results/app_test_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_videos': len(results),
            'successful': sum(1 for r in results if r['status'] == 'success'),
            'failed': sum(1 for r in results if r['status'] != 'success'),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    # Generate a simple report
    report_file = f'test_results/app_test_report_{timestamp}.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=== Application Test Report ===\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total videos tested: {len(results)}\n")
        f.write(f"Successfully processed: {sum(1 for r in results if r['status'] == 'success')}\n")
        f.write(f"Failed: {sum(1 for r in results if r['status'] != 'success')}\n\n")
        
        f.write("\n=== Detailed Results ===\n")
        for i, result in enumerate(results, 1):
            f.write(f"\nVideo {i}: {result['video_id']}\n")
            f.write(f"Status: {result['status']}\n")
            if 'response' in result:
                f.write(f"HTTP Status: {result['response']['status_code']}\n")
            if 'error' in result and result['error']:
                f.write(f"Error: {result['error']}\n")
            if 'transcript_length' in result:
                f.write(f"Transcript length: {result['transcript_length']} characters\n")
    
    print(f"\nDetailed results saved to: {os.path.abspath(output_file)}")
    print(f"Test report saved to: {os.path.abspath(report_file)}")

if __name__ == "__main__":
    main()
