from youtubesearchpython import Search
import json

def test_search():
    try:
        # Test channel videos search
        search = Search(
            "https://www.youtube.com/channel/UCzaqqlriSjVyc795m86GVyg/videos",
            limit=5,
            language='ru',
            region='RU'
        )
        
        results = search.result()
        print("Search results:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        # Print video information
        if 'result' in results:
            print("\nVideos found:")
            for i, video in enumerate(results['result'], 1):
                print(f"\n{i}. {video.get('title', 'No title')}")
                print(f"   ID: {video.get('id', 'N/A')}")
                print(f"   Duration: {video.get('duration', 'N/A')}")
                print(f"   Views: {video.get('viewCount', {}).get('text', 'N/A')}")
        else:
            print("No results found")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_search()
