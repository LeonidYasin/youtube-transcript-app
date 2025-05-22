import requests
import time

def test_server():
    # Start the server in a subprocess
    import subprocess
    import sys
    
    # Start the server
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "fastapi_server_clean:app", "--reload", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for the server to start
        print("Waiting for server to start...")
        time.sleep(5)  # Give the server time to start
        
        # Test video ID from the previous test
        test_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
        
        # Test getting Russian subtitles
        print("\nTesting Russian subtitles...")
        response = requests.get(
            "http://localhost:8000/api/transcript",
            params={"url": test_url, "language": "ru"}
        )
        
        result = response.json()
        print(f"Status: {response.status_code}")
        
        if result.get("success"):
            print(f"Success! Language: {result.get('language')}")
            print(f"First 200 chars of transcript:")
            print("-" * 50)
            print(result.get('transcript', '')[:200] + "...")
            print("-" * 50)
            
            # Save the full transcript to a file
            with open("russian_transcript.vtt", "w", encoding="utf-8") as f:
                f.write(result.get('transcript', ''))
            print("Full transcript saved to 'russian_transcript.vtt'")
        else:
            print(f"Error: {result.get('error')}")
        
    finally:
        # Stop the server
        print("\nStopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

if __name__ == "__main__":
    test_server()
