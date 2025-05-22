import requests
import json

def test_russian_transcript(video_id):
    url = "http://localhost:8080/api/transcript"
    params = {
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "language": "ru"
    }
    
    print(f"Testing Russian transcript for video: {video_id}")
    print("=" * 50)
    
    try:
        response = requests.get(url, params=params)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"\nVideo ID: {result.get('video_id')}")
            print(f"Language: {result.get('language')}")
            print(f"Is Generated: {result.get('is_generated')}")
            print("\nTranscript Preview (first 500 chars):")
            print("-" * 50)
            print(result.get('transcript', '')[:500] + "..." if result.get('transcript') else "No transcript found")
            print("-" * 50)
            
            # Save full transcript to file
            output_file = f"transcript_{video_id}_ru.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.get('transcript', ''))
            print(f"\nFull transcript saved to: {output_file}")
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error making request: {str(e)}")

if __name__ == "__main__":
    # Test with Simon Sinek's TED Talk
    test_russian_transcript("qp0HIF3SfI4")
    
    # Test with another Russian video
    # test_russian_transcript("d0n1V5qXhpo")  # Another Russian video for testing
