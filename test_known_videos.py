import os
import json
from datetime import datetime

# List of known video IDs from Rav Ginsburg's channel
KNOWN_VIDEOS = [
    "xXU4-tiX4Wk",  # The video we've been working with
    "dQw4w9WgXcQ",  # Replace with actual video IDs
    "9bZkp7q19f0",
    "KQ6zr6kCPj8",
    "JGwWNGJdvx8",
    "OPf0YbXqDm0",
    "kOkQ4T5WO9E",
    "tgbNymZ7vqY",
    "2Vv-BfVoq4g",
    "JGwWNGJdvx9",
]

def test_video(video_id: str, output_dir: str = "test_results") -> dict:
    """Test a single video and return results."""
    from app.services.youtube import YouTubeService
    
    youtube_service = YouTubeService()
    result = {
        "video_id": video_id,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "error": None,
        "transcript_available": False,
        "languages": []
    }
    
    try:
        # Get available languages
        languages = youtube_service.get_available_languages(video_id)
        result["languages"] = languages
        
        # Check if Russian is available
        if 'ru' in languages:
            result["transcript_available"] = True
            try:
                # Try to get the transcript
                transcript, _ = youtube_service.get_transcript(video_id, 'ru')
                result["success"] = True
                result["sample"] = transcript[:500]  # First 500 chars as sample
            except Exception as e:
                result["error"] = str(e)
        else:
            result["error"] = "Russian subtitles not available"
            
    except Exception as e:
        result["error"] = str(e)
    
    # Save individual result
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{video_id}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result

def main():
    results = []
    
    print(f"Testing {len(KNOWN_VIDEOS)} videos from Rav Ginsburg's channel...")
    
    for i, video_id in enumerate(KNOWN_VIDEOS, 1):
        print(f"\nTesting video {i}/{len(KNOWN_VIDEOS)}: {video_id}")
        try:
            result = test_video(video_id)
            results.append(result)
            
            # Print status
            status = "✓" if result["success"] else "✗"
            print(f"  {status} {'Russian transcript available' if result['success'] else result['error']}")
            
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    # Generate summary
    success_count = sum(1 for r in results if r["success"])
    available_count = sum(1 for r in results if r["transcript_available"])
    
    print("\n=== Summary ===")
    print(f"Total videos tested: {len(results)}")
    print(f"Videos with Russian subtitles: {available_count}")
    print(f"Successfully retrieved transcripts: {success_count}")
    
    # Save summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_videos": len(results),
        "videos_with_russian": available_count,
        "successful_retrievals": success_count,
        "results": results
    }
    
    with open("test_results/summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("\nDetailed results saved to test_results/ directory.")

if __name__ == "__main__":
    main()
