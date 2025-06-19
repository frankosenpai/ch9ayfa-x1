from fastapi import FastAPI, Query, HTTPException, Response
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
from mangum import Mangum  # باش نخدمو FastAPI كـ Serverless

app = FastAPI()

API_KEY = "ch9ayfa"

def create_fire_glow(image, border=40):
    new_width = image.width + border * 2
    new_height = image.height + border * 2
    base = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
    base.paste(image, (border, border))

    glow = base.copy()
    glow = glow.convert("L")
    glow = glow.convert("RGBA")

    r, g, b, a = glow.split()
    r = r.point(lambda i: min(255, int(i * 3)))
    g = g.point(lambda i: min(255, int(i * 1.5)))
    b = b.point(lambda i: int(i * 0.1))
    glow_colored = Image.merge("RGBA", (r, g, b, a))

    glow_blurred = glow_colored.filter(ImageFilter.GaussianBlur(radius=30))

    result = Image.alpha_composite(glow_blurred, base)

    return result

def add_watermark(base_image, text="@CH9AYFAX1", position=(20,20), opacity=100, font_path="arial.ttf", font_size=40):
    watermark = Image.new("RGBA", base_image.size, (0,0,0,0))
    draw = ImageDraw.Draw(watermark)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    fill_color = (255, 255, 255, opacity)

    draw.text(position, text, font=font, fill=fill_color)

    combined = Image.alpha_composite(base_image, watermark)
    return combined

@app.get("/outfit-image")
def get_outfit(uid: str = Query(...), region: str = Query(...), key: str = Query(None)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    url = f"https://aditya-outfit-v6op.onrender.com/outfit-image?uid={uid}&region={region}"

    try:
        res = requests.get(url, timeout=20)
        if res.status_code != 200 or not res.headers.get("content-type", "").startswith("image"):
            raise HTTPException(status_code=400, detail="Image not found or invalid response")

        original = Image.open(BytesIO(res.content)).convert("RGBA")

        fire_img = create_fire_glow(original, border=40)

        final_img = add_watermark(fire_img, opacity=100)

        output = BytesIO()
        final_img.save(output, format="PNG")
        output.seek(0)

        return Response(content=output.getvalue(), media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


handler = Mangum(app)



