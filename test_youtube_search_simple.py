import asyncio
from typing import List, Dict
from youtube_search import YoutubeSearch

def search_youtube_channels(query: str, max_results: int = 5) -> dict:
    try:
        print(f"Searching for: {query}")
        
        # Search for channels
        results = YoutubeSearch(query, max_results=max_results).to_dict()
        
        channels = []
        for item in results:
            if 'channel' in item.get('url_suffix', ''):
                channel_info = {
                    "title": item.get('title', '').replace(' - YouTube', ''),
                    "url": f"https://www.youtube.com{item.get('url_suffix', '')}",
                    "description": item.get('long_desc', ''),
                    "duration": item.get('duration', ''),
                    "views": item.get('views', '')
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

def main():
    # Test search
    queries = ["рав гинзбург", "python programming"]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Testing search for: {query}")
        
        result = search_youtube_channels(query)
        
        print("\nSearch Results:")
        print(f"Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            print(f"Found {result.get('count')} channels:")
            for idx, channel in enumerate(result.get('results', []), 1):
                print(f"\n{idx}. {channel.get('title')}")
                print(f"   URL: {channel.get('url')}")
                print(f"   Description: {channel.get('description')[:100]}..." if channel.get('description') else "")
        else:
            print(f"Error: {result.get('message')}")

if __name__ == "__main__":
    main()
