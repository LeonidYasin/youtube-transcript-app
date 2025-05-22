import asyncio
from pytube import Search
from typing import List, Dict

async def search_youtube_channels(query: str, max_results: int = 5) -> dict:
    try:
        print(f"Searching for channels with query: {query}")
        search = Search(query)
        
        # Get the first page of results
        results = search.results
        
        channels = []
        for item in results[:max_results]:
            if hasattr(item, 'channel_id'):  # This is a channel
                channel_info = {
                    "channel_id": item.channel_id,
                    "title": item.title,
                    "description": item.description,
                    "url": f"https://www.youtube.com{item.url}"
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
            "message": str(e),
            "error_type": str(type(e).__name__)
        }

async def main():
    # Test search
    queries = ["рав гинзбург", "python programming"]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Testing search for: {query}")
        
        result = await search_youtube_channels(query)
        
        print("\nSearch Results:")
        print(f"Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            print(f"Found {result.get('count')} channels:")
            for idx, channel in enumerate(result.get('results', []), 1):
                print(f"\n{idx}. {channel.get('title')}")
                print(f"   URL: {channel.get('url')}")
                print(f"   Channel ID: {channel.get('channel_id')}")
        else:
            print(f"Error: {result.get('message')}")
            print(f"Error type: {result.get('error_type')}")

if __name__ == "__main__":
    asyncio.run(main())
