import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

def download_transcript(video_id, language_code='ru'):
    """Download transcript directly from YouTube's API"""
    # Base URL for YouTube's timedtext API
    base_url = "https://www.youtube.com/api/timedtext"
    
    # Parameters for the request - using the same parameters as seen in the browser
    params = {
        'v': video_id,
        'ei': 'gfEsaIOFFqWAkucP3NKogAg',  # This seems to be a session ID
        'caps': 'asr',  # Automatic Speech Recognition
        'opi': '112496729',  # Some internal YouTube parameter
        'xoaf': '5',  # Another internal parameter
        'hl': 'en',  # Interface language
        'ip': '0.0.0.0',  # IP address
        'ipbits': '0',  # IP bits
        'expire': '1747801073',  # Expiration timestamp
        'sparams': 'ip,ipbits,expire,v,ei,caps,opi,xoaf',  # Parameters to sign
        'signature': 'D36200E3A66F6E65D18A85A65D3B6BB36790B68B.E17F30AB76ED7C06C6F972EC6FC29516B2DAE9E6',  # Signature
        'key': 'yt8',  # API key
        'lang': language_code,  # Language code
        'fmt': 'srv3',  # Format (srv3 includes timing information)
        'xorb': '2',  # Additional parameter
        'xobt': 'True',  # Additional parameter
        'xovt': '3',  # Additional parameter
    }
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': f'https://www.youtube.com/watch?v={video_id}',
        'Origin': 'https://www.youtube.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    
    try:
        # Make the request
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save the raw response
        with open(f'transcript_{language_code}.xml', 'wb') as f:
            f.write(response.content)
        print(f"Saved raw transcript to transcript_{language_code}.xml")
        
        # Parse the XML response
        try:
            root = ET.fromstring(response.content)
            
            # Extract text from all <text> elements
            transcript_texts = []
            for elem in root.findall('.//text'):
                if elem.text:
                    transcript_texts.append(elem.text.strip())
            
            # Join all text segments with newlines
            full_transcript = '\n'.join(transcript_texts)
            
            # Save the cleaned transcript
            with open(f'transcript_{language_code}.txt', 'w', encoding='utf-8') as f:
                f.write(full_transcript)
            
            print(f"Successfully extracted {len(transcript_texts)} text segments")
            print(f"Saved transcript to transcript_{language_code}.txt")
            
            # Print the first few lines as a preview
            print("\nPreview of the transcript:")
            print('\n'.join(transcript_texts[:5]))
            
            return full_transcript
            
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            print("Trying to handle malformed XML...")
            
            # Try to extract text even if XML is malformed
            import re
            text_matches = re.findall(r'<text[^>]*>(.*?)</text>', response.text, re.DOTALL)
            if text_matches:
                with open(f'transcript_{language_code}_fallback.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(text_matches))
                print(f"Saved fallback transcript to transcript_{language_code}_fallback.txt")
                return '\n'.join(text_matches)
            
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error downloading transcript: {e}")
        return None

if __name__ == "__main__":
    video_id = "qp0HIF3SfI4"  # The problematic video
    language_code = "ru"  # Russian
    
    print(f"Downloading {language_code} transcript for video {video_id}...")
    transcript = download_transcript(video_id, language_code)
    
    if transcript:
        print("\nTranscript download successful!")
    else:
        print("\nFailed to download transcript.")
