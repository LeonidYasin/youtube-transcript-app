"""
Script to find Kabbalah-related YouTube videos with available transcripts.
"""
import json
import sys
import io
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# Set console to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# List of Kabbalah-related video IDs to check - using more reliable sources
KABBALAH_VIDEOS = [
    # Kabbalah Center videos (official channel)
    {"id": "9dBk2VQ8aXQ", "langs": ["en", "ru", "he"], "name": "Introduction to Kabbalah"},
    
    # Michael Laitman's channel (popular Kabbalah teacher)
    {"id": "k85mRPqvMbE", "langs": ["en", "he", "ru"], "name": "What is Kabbalah?"},
    
    # More reliable Kabbalah videos
    {"id": "Y8yIJDEC0sQ", "langs": ["en"], "name": "The Power of Kabbalah"},
    
    # Kabbalah in Russian
    {"id": "QxZMGiy6zsE", "langs": ["ru"], "name": "Основы Каббалы"},
    
    # Kabbalah in Hebrew
    {"id": "fRbq3WfWY1M", "langs": ["he"], "name": "יסודות הקבלה"},
    
    # More general Kabbalah content
    {"id": "J9VQTm7yTsY", "langs": ["en"], "name": "Kabbalah and Spirituality"}
]

def check_video_transcripts():
    """Check which Kabbalah videos have available transcripts."""
    results = []
    
    for video in KABBALAH_VIDEOS:
        video_id = video["id"]
        target_langs = video["langs"]
        name = video["name"]
        
        print(f"\nChecking: {name}")
        print(f"URL: https://youtu.be/{video_id}")
        print(f"Target languages: {', '.join(target_langs)}")
        
        try:
            # List all available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Get available languages
            available_langs = [t.language_code for t in transcript_list]
            print(f"Available transcripts: {', '.join(available_langs) or 'None'}")
            
            found = False
            
            # Try each target language in order
            for lang in target_langs:
                try:
                    # Try to get the transcript in the current language
                    transcript = transcript_list.find_transcript([lang])
                    print(f"✅ Found {lang} transcript")
                    
                    # Get the transcript text
                    transcript_text = transcript.fetch()
                    formatter = TextFormatter()
                    formatted_text = formatter.format_transcript(transcript_text)
                    
                    results.append({
                        "id": video_id,
                        "name": name,
                        "language": lang,
                        "status": "success",
                        "available_languages": available_langs,
                        "transcript_length": len(formatted_text),
                        "sample": formatted_text[:200] + ("..." if len(formatted_text) > 200 else ""),
                        "url": f"https://youtu.be/{video_id}"
                    })
                    
                    found = True
                    break  # Found a working language, no need to check others
                    
                except Exception as e:
                    print(f"❌ No {lang} transcript: {str(e)}")
            
            # If no target languages worked, try any available language
            if not found and available_langs:
                try:
                    # Try the first available language
                    lang = available_langs[0]
                    transcript = transcript_list.find_transcript([lang])
                    print(f"⚠️  Using {lang} transcript (fallback)")
                    
                    transcript_text = transcript.fetch()
                    formatter = TextFormatter()
                    formatted_text = formatter.format_transcript(transcript_text)
                    
                    results.append({
                        "id": video_id,
                        "name": name,
                        "language": lang,
                        "status": "fallback",
                        "available_languages": available_langs,
                        "transcript_length": len(formatted_text),
                        "sample": formatted_text[:200] + ("..." if len(formatted_text) > 200 else ""),
                        "url": f"https://youtu.be/{video_id}"
                    })
                    
                except Exception as e:
                    print(f"❌ Could not use fallback language: {str(e)}")
                    results.append({
                        "id": video_id,
                        "name": name,
                        "status": "no_transcript",
                        "available_languages": available_langs,
                        "error": str(e),
                        "url": f"https://youtu.be/{video_id}"
                    })
                    
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error checking video: {error_msg}")
            results.append({
                "id": video_id,
                "name": name,
                "status": "error",
                "error": error_msg,
                "url": f"https://youtu.be/{video_id}"
            })
    
    # Save results to a file
    with open("kabbalah_videos_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\nResults saved to kabbalah_videos_results.json")
    
    # Print summary
    success = len([r for r in results if r["status"] == "success"])
    not_found = len([r for r in results if r["status"] == "not_found"])
    errors = len([r for r in results if r["status"] == "error"])
    
    print(f"\nSummary:")
    print(f"✅ Success: {success}")
    print(f"❌ Not found: {not_found}")
    print(f"⚠️  Errors: {errors}")
    
    if success > 0:
        print("\nVideos with transcripts:")
        for r in [r for r in results if r["status"] == "success"]:
            print(f"- {r['name']} ({r['language']}): {r['url']}")

if __name__ == "__main__":
    print("Searching for Kabbalah videos with available transcripts...")
    check_video_transcripts()
