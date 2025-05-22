import requests
from urllib.parse import quote_plus
import re
import sys
import io

# Set stdout to handle UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def search_youtube(query, max_results=5):
    """Search YouTube and return results"""
    try:
        # Encode the search query
        query_encoded = quote_plus(query)
        
        # Construct the search URL
        url = f"https://www.youtube.com/results?search_query={query_encoded}&sp=EgIQAg%3D%3D"  # Filters to channels only
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Extract channel information using regex
        channel_pattern = r'"channelRenderer":{"channelId":"([^"]+)".*?"title":{"simpleText":"([^"]+)"'
        matches = re.findall(channel_pattern, response.text)
        
        # Format the results
        results = []
        for channel_id, title in matches[:max_results]:
            results.append({
                'channel_id': channel_id,
                'title': title,
                'url': f'https://www.youtube.com/channel/{channel_id}'
            })
        
        return {
            'status': 'success',
            'query': query,
            'results': results,
            'count': len(results)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'error_type': type(e).__name__
        }

def main():
    # Test search
    queries = ["рав гинзбург", "python programming"]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Testing search for: {query}")
        
        result = search_youtube(query)
        
        print("\nSearch Results:")
        print(f"Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            print(f"Found {result.get('count')} channels:")
            for idx, channel in enumerate(result.get('results', []), 1):
                try:
                    print(f"\n{idx}. {channel.get('title')}")
                    print(f"   URL: {channel.get('url')}")
                except UnicodeEncodeError:
                    # Fallback for console encoding issues
                    print(f"\n{idx}. [Channel with non-ASCII characters]")
                    print(f"   URL: {channel.get('url')}")
        else:
            print(f"Error: {result.get('message')}")

if __name__ == "__main__":
    main()
