from fastapi import FastAPI, Query, HTTPException, Response
import requests

app = FastAPI()

API_KEY = "ch9ayfa"

@app.get("/outfit-image")
def get_outfit(uid: str = Query(...), region: str = Query(...), key: str = Query(None)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    url = f"https://aditya-outfit-v6op.onrender.com/outfit-image?uid={uid}&region={region}"

    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and res.headers.get("content-type", "").startswith("image"):
            return Response(content=res.content, media_type=res.headers["content-type"])
        else:
            raise HTTPException(status_code=400, detail="Image not found or invalid response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
