import requests
from urllib.parse import quote_plus, urlparse, parse_qs
import re
from typing import List, Dict, Optional, Any
from datetime import datetime

class YouTubeSearcher:
    @staticmethod
    def search_channels(query: str, max_results: int = 5) -> dict:
        """
        Search for YouTube channels by query
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (max 20)
            
        Returns:
            Dictionary containing search results
        """
        try:
            # Encode the search query
            query_encoded = quote_plus(query)
            
            # Construct the search URL (filtering for channels)
            url = f"https://www.youtube.com/results?search_query={query_encoded}&sp=EgIQAg%3D%3D"
            
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8,he;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            }
            
            # Make the request with a session
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extract channel information using regex
            channel_pattern = r'"channelRenderer":\{"channelId":"([^"]+)".*?"title":\{"simpleText":"([^"]+)"'
            matches = re.findall(channel_pattern, response.text)
            
            # If no matches found, try alternative pattern
            if not matches:
                channel_pattern = r'"channelId":"([^"]+)".*?"title":\{"runs":\[\{"text":"([^"]+)"'
                matches = re.findall(channel_pattern, response.text)
            
            # Format the results
            results = []
            for channel_id, title in matches[:max_results]:
                # Skip shorts and other non-channel results
                if 'shorts' in channel_id.lower() or not channel_id.startswith('UC'):
                    continue
                    
                results.append({
                    'channel_id': channel_id,
                    'title': title,
                    'url': f'https://www.youtube.com/channel/{channel_id}'
                })
            
            if not results:
                return {
                    'status': 'error',
                    'message': 'No channels found matching the search criteria',
                    'error_type': 'NoResultsError'
                }
                
            return {
                'status': 'success',
                'query': query,
                'results': results,
                'count': len(results)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f'Network error occurred: {str(e)}',
                'error_type': 'NetworkError'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'An error occurred: {str(e)}',
                'error_type': type(e).__name__
            }
    
    @staticmethod
    def find_rabbi_ginsburgh_channel() -> Optional[Dict]:
        """
        Specifically search for Rabbi Yitzchak Ginsburgh's official channel
        """
        searches = [
            "יצחק גינזבורג",
            "Yitzchak Ginsburgh",
            "Рав Гинзбург",
            "Рав Ицхак Гинзбург",
            "הרב יצחק גינזבורג"
        ]
        
        for query in searches:
            result = YouTubeSearcher.search_channels(query, max_results=5)
            if result['status'] == 'success' and result['count'] > 0:
                # Look for the most likely official channel
                official_keywords = ['הרב', 'גל', 'עיני', 'יצחק', 'גינזבורג', 'הרצאות', 'הרב יצחק', 'ginsburgh']
                
                for channel in result['results']:
                    title = channel['title'].lower()
                    if any(keyword.lower() in title for keyword in official_keywords):
                        return channel
                
                # If no exact match, return the first result
                return result['results'][0]
        
        return None
        
    @staticmethod
    def get_channel_videos(channel_id: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Get the latest videos from a YouTube channel using the channel's videos page
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to return (max 50)
            
        Returns:
            Dictionary containing the list of videos and metadata
        """
        try:
            # Directly access the channel's videos page
            videos_url = f"https://www.youtube.com/channel/{channel_id}/videos"
            
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8,he;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            
            # Get the channel's videos page
            response = requests.get(videos_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extract video information using regex
            # This pattern looks for video entries in the page
            video_pattern = r'"videoId":"([^"]+)".*?"title":\{"runs":\[\{"text":"([^"]+)"\}.*?"lengthText":\{"accessibility":\{"accessibilityData":\{"label":"([^"]+)"\}\}.*?"simpleText":"([^"]+)"\}.*?"viewCountText":\{"simpleText":"([^"]+)"\}.*?"publishedTimeText":\{"simpleText":"([^"]+)"\}'
            video_matches = re.findall(video_pattern, response.text, re.DOTALL)
            
            if not video_matches:
                # Try alternative pattern if the first one doesn't match
                alt_pattern = r'"videoId":"([^"]+)".*?"title":\{"runs":\[\{"text":"([^"]+)"\}.*?"simpleText":"([^"]+)"\}.*?"viewCountText":\{"simpleText":"([^"]+)"\}.*?"publishedTimeText":\{"simpleText":"([^"]+)"\}'
                video_matches = re.findall(alt_pattern, response.text, re.DOTALL)
                
                if not video_matches:
                    return {
                        'status': 'error',
                        'message': 'Could not extract video information from the channel page',
                        'error_type': 'VideoExtractionError'
                    }
                
                # Format for the alternative pattern (without duration)
                videos = []
                for video_id, title, view_count, published_time in video_matches[:max_results]:
                    videos.append({
                        'video_id': video_id,
                        'title': title.replace('\n', ' ').strip(),
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                        'duration': 'N/A',
                        'view_count': view_count,
                        'published_time': published_time,
                        'thumbnail': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
                    })
            else:
                # Format for the original pattern (with duration)
                videos = []
                for video_id, title, duration, duration_text, view_count, published_time in video_matches[:max_results]:
                    videos.append({
                        'video_id': video_id,
                        'title': title.replace('\n', ' ').strip(),
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                        'duration': duration_text,
                        'view_count': view_count,
                        'published_time': published_time,
                        'thumbnail': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
                    })
            
            return {
                'status': 'success',
                'channel_id': channel_id,
                'videos': videos,
                'count': len(videos)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'error_type': type(e).__name__
            }
