from youtubesearchpython import VideosSearch
import json
import os

def search_videos(query: str, limit: int = 10) -> list:
    """Search for videos on YouTube."""
    videos_search = VideosSearch(query, limit=limit)
    results = videos_search.result()['result']
    
    videos = []
    for video in results:
        videos.append({
            'id': video['id'],
            'title': video['title'],
            'channel': video['channel']['name'],
            'duration': video.get('duration', 'N/A'),
            'views': video.get('viewCount', {}).get('text', 'N/A'),
            'published_time': video.get('publishedTime', 'N/A')
        })
    
    return videos

def save_videos_to_test(videos: list):
    """Save video IDs to a test file."""
    video_ids = [video['id'] for video in videos]
    
    # Create a test script
    test_script = """from test_multiple_videos import test_multiple_videos

# List of video IDs to test
video_ids = {}

# Run tests
test_multiple_videos(video_ids)
""".format(json.dumps(video_ids, indent=4))
    
    with open('test_videos.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print(f"\nCreated test script with {len(video_ids)} videos.")
    print("Run 'python test_videos.py' to start testing.")

if __name__ == "__main__":
    # Search for Rav Ginsburg videos
    QUERY = "Рав Гинзбург"  # Search query in Russian
    LIMIT = 10
    
    print(f"Searching for videos with query: '{QUERY}'")
    videos = search_videos(QUERY, limit=LIMIT)
    
    # Save results
    os.makedirs('test_results', exist_ok=True)
    output_file = 'test_results/videos_found.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print(f"\nFound {len(videos)} videos. Results saved to {output_file}")
    print("\nVideos found:")
    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['title']} (ID: {video['id']})")
    
    # Create test script
    save_videos_to_test(videos)
