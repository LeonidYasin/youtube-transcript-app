from youtubesearchpython import Search, VideoSortOrder
import json
import os

def get_channel_videos(channel_handle: str, limit: int = 10) -> list:
    """Get recent videos from a channel."""
    search = Search(
        f"https://www.youtube.com/@{channel_handle}/videos",
        limit=limit,
        language='en',
        region='US'
    )
    
    videos = []
    results = search.result()['result']
    
    for video in results:
        if len(videos) >= limit:
            break
        videos.append({
            'id': video['id'],
            'title': video['title'],
            'published': video.get('publishedTime', 'N/A'),
            'duration': video.get('duration', 'N/A'),
            'views': video.get('viewCount', {}).get('text', 'N/A')
        })
    
    return videos

if __name__ == "__main__":
    # Rav Ginsburg's channel handle
    CHANNEL_HANDLE = "RavGinsburg"
    
    print(f"Fetching videos from channel: {CHANNEL_HANDLE}")
    videos = get_channel_videos(CHANNEL_HANDLE, limit=10)
    
    # Save to file
    os.makedirs('test_results', exist_ok=True)
    output_file = 'test_results/channel_videos.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    
    print(f"\nFound {len(videos)} videos. Results saved to {output_file}")
    print("\nVideo IDs:")
    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['id']} - {video['title']} ({video['duration']})")
