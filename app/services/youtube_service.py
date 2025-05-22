from typing import List, Dict, Optional, Any
import logging
import json
import re
import os
import yt_dlp
from urllib.parse import quote_plus

# Configure logging
logger = logging.getLogger(__name__)
# Disable proxy for requests
os.environ['no_proxy'] = '*'

def get_channel_videos_ytdlp(channel_id: str, max_results: int = 10) -> List[Dict]:
    """
    Get videos from a YouTube channel using yt-dlp
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'force_generic_extractor': True,
            'skip_download': True,
            'extract_flat': 'in_playlist',
            'playlistend': max_results,
        }
        
        # Try to get videos from the channel's videos page
        url = f'https://www.youtube.com/channel/{channel_id}/videos'
        videos = []
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            
            if 'entries' in result:
                for entry in result['entries']:
                    if len(videos) >= max_results:
                        break
                        
                    try:
                        video_id = entry.get('id', '')
                        if not video_id:
                            continue
                            
                        # Get the highest resolution thumbnail
                        thumbnails = entry.get('thumbnails', [])
                        thumbnail = thumbnails[-1]['url'] if thumbnails else ''
                        
                        videos.append({
                            'video_id': video_id,
                            'title': entry.get('title', 'Без названия'),
                            'duration': str(entry.get('duration', 'N/A')),
                            'published_time': entry.get('upload_date', ''),
                            'view_count': str(entry.get('view_count', 'N/A')),
                            'thumbnail': thumbnail
                        })
                        
                    except Exception as e:
                        logger.error(f"Error processing video entry: {str(e)}")
                        continue
        
        return videos
        
    except Exception as e:
        logger.error(f"Error getting channel videos with yt-dlp: {str(e)}")
        return []

class YouTubeService:
    async def search_channels(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Поиск каналов на YouTube
        
        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов
            
        Returns:
            Список словарей с информацией о каналах
        """
        try:
            search = ChannelsSearch(query, limit=max_results)
            results = search.result()["result"]
            
            channels = []
            for channel in results:
                channels.append({
                    "channel_id": channel["id"],
                    "title": channel["title"],
                    "description": channel.get("description", ""),
                    "subscribers": channel.get("subscribers", "N/A"),
                    "video_count": channel.get("videoCount", "N/A"),
                    "thumbnail": channel["thumbnails"][0]["url"] if channel.get("thumbnails") else None
                })
            
            return channels
            
        except Exception as e:
            raise Exception(f"Ошибка при поиске каналов: {str(e)}")

    async def get_channel_videos(self, channel_id: str, max_results: int = 10) -> List[Dict]:
        """
        Получение списка видео канала
        
        Args:
            channel_id: ID канала
            max_results: Максимальное количество видео
            
        Returns:
            Список словарей с информацией о видео
        """
        try:
            logger.info(f"Fetching videos for channel: {channel_id}")
            
            # Get videos from the channel using yt-dlp
            videos = get_channel_videos_ytdlp(channel_id, max_results)
            
            if not videos:
                logger.warning(f"No videos found for channel: {channel_id}")
                return []
                
            logger.info(f"Successfully fetched {len(videos)} videos for channel: {channel_id}")
            return videos
            
        except Exception as e:
            error_msg = f"Error fetching channel videos: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
