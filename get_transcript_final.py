import yt_dlp
import os
import json

def save_to_file(filename, content):
    """Helper function to save content to a file with UTF-8 encoding"""
    with open(filename, 'w', encoding='utf-8') as f:
        if isinstance(content, dict):
            json.dump(content, f, ensure_ascii=False, indent=2)
        else:
            f.write(str(content))

def get_transcript(video_url, language='ru'):
    """Get transcript and save all information to files"""
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [language],
        'outtmpl': 'subtitles/%(id)s',
        'quiet': True,
        'no_warnings': False,
    }
    
    try:
        os.makedirs('subtitles', exist_ok=True)
        results = {}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            info_dict = ydl.extract_info(video_url, download=False)
            video_id = info_dict.get('id', 'unknown')
            results['video_info'] = {
                'id': video_id,
                'title': info_dict.get('title', 'Unknown'),
                'duration': info_dict.get('duration', 0),
                'uploader': info_dict.get('uploader', 'Unknown'),
                'upload_date': info_dict.get('upload_date', 'Unknown'),
                'view_count': info_dict.get('view_count', 0),
                'like_count': info_dict.get('like_count', 0),
                'categories': info_dict.get('categories', []),
                'tags': info_dict.get('tags', []),
            }
            
            # Save all available subtitles info
            available_subs = info_dict.get('subtitles', {})
            auto_subs = info_dict.get('automatic_captions', {})
            results['available_subtitles'] = {
                'manual': list(available_subs.keys()),
                'auto': list(auto_subs.keys())
            }
            
            # Save detailed info about Russian subtitles if available
            if language in available_subs or language in auto_subs:
                results['russian_subtitles'] = {
                    'manual': available_subs.get(language, []),
                    'auto': auto_subs.get(language, [])
                }
                
                # Try to download the subtitles
                try:
                    ydl.download([video_url])
                    
                    # Check for downloaded subtitle files
                    sub_files = [f for f in os.listdir('subtitles') if f.startswith(video_id)]
                    results['downloaded_files'] = sub_files
                    
                    # Read and save the content of each subtitle file
                    for file in sub_files:
                        try:
                            with open(os.path.join('subtitles', file), 'r', encoding='utf-8') as f:
                                results[f'content_{file}'] = f.read()
                        except Exception as e:
                            results[f'error_{file}'] = str(e)
                            
                except Exception as e:
                    results['download_error'] = str(e)
            else:
                results['error'] = f"No {language} subtitles found"
            
            # Save all results to files
            save_to_file('results.json', results)
            save_to_file('full_info.json', info_dict)
            
            # Create a simple text summary
            summary = f"""=== Video Information ===
Title: {results['video_info']['title']}
ID: {results['video_info']['id']}
Duration: {results['video_info']['duration']} seconds
Uploader: {results['video_info']['uploader']}
Upload Date: {results['video_info']['upload_date']}
Views: {results['video_info']['view_count']:,}
Likes: {results['video_info'].get('like_count', 'N/A')}

=== Available Subtitles ===
Manual: {', '.join(results['available_subtitles']['manual']) or 'None'}
Auto: {', '.join(results['available_subtitles']['auto']) or 'None'}
"""
            
            if 'russian_subtitles' in results:
                summary += f"\n=== Russian Subtitles ===\n"
                if results['russian_subtitles']['manual']:
                    summary += "Manual subtitles available\n"
                if results['russian_subtitles']['auto']:
                    summary += "Auto-generated subtitles available\n"
            
            if 'downloaded_files' in results and results['downloaded_files']:
                summary += f"\n=== Downloaded Files ===\n"
                for file in results['downloaded_files']:
                    summary += f"- {file}\n"
                
                # Add a preview of the first subtitle file
                first_file = results['downloaded_files'][0]
                if f'content_{first_file}' in results:
                    preview = results[f'content_{first_file}']
                    preview_lines = preview.split('\n')[:10]  # First 10 lines
                    summary += "\n=== Preview ===\n" + '\n'.join(preview_lines)
            
            save_to_file('summary.txt', summary)
            print("Results have been saved to results.json, full_info.json, and summary.txt")
            
            return results
            
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        save_to_file('error.txt', error_msg)
        print(error_msg)
        return None

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
    print(f"Fetching transcript for: {video_url}")
    result = get_transcript(video_url, 'ru')
