from fastapi import FastAPI, Query, Response
import requests

app = FastAPI()

API_KEY = "ch9ayfa"  # المفتاح السري

@app.get("/outfit-image")
def get_outfit_image(
    uid: str = Query(...), 
    region: str = Query(...), 
    key: str = Query(None)
):
    if key != API_KEY:
        return {"error": "🔐 Invalid API key!"}

    try:
        url = f"https://aditya-outfit-v6op.onrender.com/outfit-image?uid={uid}&region={region}"
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            return Response(content=r.content, media_type="image/png")
        else:
            return {"error": f"❌ Failed to fetch image. Status code: {r.status_code}"}

    except Exception as e:
        return {"error": f"❌ Exception: {str(e)}"}
