from fastapi import FastAPI, HTTPException, Query
from fastapi.testclient import TestClient
from youtubesearchpython import ChannelsSearch
from typing import List, Dict
import uvicorn

app = FastAPI()

@app.get("/search")
async def search_channels(query: str, max_results: int = 10):
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
        
        return {"status": "success", "results": channels, "count": len(channels)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("test_youtube_search:app", host="127.0.0.1", port=8000, reload=True)
