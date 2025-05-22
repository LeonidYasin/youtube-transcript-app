"""
Test script to check different versions of youtube-transcript-api.
"""
import subprocess
import sys
import json
import importlib
from typing import List, Tuple, Optional, Dict, Any

def test_version(version: str, video_id: str, language: str = 'iw') -> Tuple[bool, str]:
    """Test a specific version of youtube-transcript-api."""
    print(f"\nTesting version {version}...")
    
    # Install the specific version
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", f"youtube-transcript-api=={version}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return False, f"Failed to install version {version}"
    
    # Reload the module to ensure we're using the correct version
    if 'youtube_transcript_api' in sys.modules:
        importlib.reload(sys.modules['youtube_transcript_api'])
    
    # Test the version
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Try to list transcripts (handles different API versions)
        try:
            # For newer versions
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            print(f"Available transcripts for version {version}:")
            
            # Print available transcripts
            print("  Manual transcripts:")
            for transcript in transcript_list:
                print(f"    - {transcript.language} ({transcript.language_code})")
            
            # Try to access generated transcripts if available
            if hasattr(transcript_list, '_generated_transcripts'):
                print("  Generated transcripts:")
                for transcript in transcript_list._generated_transcripts:
                    print(f"    - {transcript.language} ({transcript.language_code})")
            
        except Exception as e:
            print(f"  Could not list transcripts: {str(e)}")
        
        # Try to get the transcript
        try:
            print(f"  Attempting to get transcript in {language}...")
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=[language],
                preserve_formatting=True
            )
            return True, f"Successfully retrieved {len(transcript)} entries"
        except Exception as e:
            return False, f"Failed to get transcript: {str(e)}"
            
    except Exception as e:
        return False, f"Error with version {version}: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_transcript_versions.py <video_id> [language]")
        return
    
    video_id = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'iw'
    
    # Test different versions (from newest to oldest)
    versions = [
        '0.6.3', '0.6.2', '0.6.1', '0.6.0',
        '0.5.2', '0.5.1', '0.5.0',
        '0.4.1', '0.4.0',
        '0.3.5', '0.3.4', '0.3.3', '0.3.2', '0.3.1', '0.3.0',
        '0.2.1', '0.2.0',
        '0.1.9', '0.1.8', '0.1.7', '0.1.6', '0.1.5', '0.1.4', '0.1.3', '0.1.2', '0.1.1'
    ]
    
    results = {}
    
    print(f"Testing video: {video_id} (language: {language})")
    print("=" * 50)
    
    for version in versions:
        success, message = test_version(version, video_id, language)
        results[version] = {
            'success': success,
            'message': message
        }
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for version, result in results.items():
        status = "SUCCESS" if result['success'] else "FAILED"
        print(f"{version}: {status} - {result['message']}")

if __name__ == "__main__":
    main()
