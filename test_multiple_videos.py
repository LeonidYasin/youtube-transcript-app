import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import our existing services
from app.services.youtube import YouTubeService

# Initialize the YouTube service
youtube_service = YouTubeService()

def test_video(video_id: str, output_dir: str = "test_results") -> Dict[str, Any]:
    """Test a single video and return results."""
    result = {
        "video_id": video_id,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "error": None,
        "transcript": None,
        "languages": [],
        "metadata": {}
    }
    
    try:
        # Get video metadata
        metadata = youtube_service.get_video_metadata(video_id)
        result["metadata"].update(metadata)
        
        # Get available languages
        languages = youtube_service.get_available_languages(video_id)
        result["languages"] = languages
        
        # Try to get Russian transcript
        if 'ru' in languages:
            transcript, _ = youtube_service.get_transcript(video_id, 'ru')
            result["transcript"] = transcript
            result["success"] = True
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

def test_multiple_videos(video_ids: List[str], output_file: str = "test_results/summary.json"):
    """Test multiple videos and save summary."""
    results = []
    
    for i, video_id in enumerate(video_ids, 1):
        print(f"\nTesting video {i}/{len(video_ids)}: {video_id}")
        try:
            result = test_video(video_id)
            results.append(result)
            
            # Save progress after each video
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_videos": len(video_ids),
                    "completed": i,
                    "results": results
                }, f, ensure_ascii=False, indent=2)
                
            # Be nice to YouTube's servers
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing video {video_id}: {str(e)}")
    
    # Generate summary
    success_count = sum(1 for r in results if r["success"])
    print(f"\nTesting complete! Successfully processed {success_count} out of {len(video_ids)} videos.")
    
    # Print summary
    print("\n=== Summary ===")
    for result in results:
        status = "✓" if result["success"] else "✗"
        title = result.get("metadata", {}).get("title", "Unknown title")
        print(f"{status} {result['video_id']}: {title}")
        if not result["success"]:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    return results

if __name__ == "__main__":
    # List of video IDs from Rav Ginsburg's channel
    video_ids = [
        "xXU4-tiX4Wk",  # The video we've been working with
        "dQw4w9WgXcQ",  # Example ID 1 (replace with actual IDs)
        "9bZkp7q19f0",  # Example ID 2
        "KQ6zr6kCPj8",  # Example ID 3
        "JGwWNGJdvx8",  # Example ID 4
        "OPf0YbXqDm0",  # Example ID 5
        "kOkQ4T5WO9E",  # Example ID 6
        "tgbNymZ7vqY",  # Example ID 7
        "2Vv-BfVoq4g",  # Example ID 8
        "JGwWNGJdvx9",  # Example ID 9
    ]
    
    # Run tests
    test_multiple_videos(video_ids)
