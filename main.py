from fastapi import FastAPI, Query, HTTPException, Response
import requests

app = FastAPI()

API_KEY = "ch9ayfa"

@app.get("/outfit-image")
def outfit_image(uid: str = Query(...), region: str = Query(...), key: str = Query(None)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    external_url = f"https://aditya-outfit-v6op.onrender.com/outfit-image?uid={uid}&region={region}"

    try:
        response = requests.get(external_url, timeout=15)
        if response.status_code == 200 and response.headers.get("content-type", "").startswith("image"):
            return Response(content=response.content, media_type=response.headers["content-type"])
        else:
            raise HTTPException(status_code=502, detail="Failed to fetch image from source")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

