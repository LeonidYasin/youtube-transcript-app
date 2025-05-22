import asyncio
from youtubesearchpython import ChannelsSearch

async def search_youtube_channels(query: str, max_results: int = 5) -> dict:
    try:
        print(f"Searching for channels with query: {query}")
        search = ChannelsSearch(query, limit=max_results)
        results = search.result()["result"]
        
        channels = []
        for channel in results:
            channel_info = {
                "channel_id": channel.get("id", ""),
                "title": channel.get("title", ""),
                "description": channel.get("description", ""),
                "subscribers": channel.get("subscribers", "N/A"),
                "video_count": channel.get("videoCount", "N/A"),
                "thumbnail": channel["thumbnails"][0]["url"] if channel.get("thumbnails") else None
            }
            channels.append(channel_info)
        
        return {
            "status": "success",
            "query": query,
            "results": channels,
            "count": len(channels)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

async def main():
    # Test search
    query = "рав гинзбург"
    print(f"Testing search for: {query}")
    
    result = await search_youtube_channels(query)
    
    print("\nSearch Results:")
    print(f"Status: {result.get('status')}")
    
    if result.get('status') == 'success':
        print(f"Found {result.get('count')} channels:")
        for idx, channel in enumerate(result.get('results', []), 1):
            print(f"\n{idx}. {channel.get('title')}")
            print(f"   Subscribers: {channel.get('subscribers')}")
            print(f"   Videos: {channel.get('video_count')}")
            print(f"   Channel ID: {channel.get('channel_id')}")
    else:
        print(f"Error: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(main())
