from fastapi import FastAPI, Query, HTTPException, Response
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO

app = FastAPI()

API_KEY = "ch9ayfa"

def create_fire_glow(image, border=40):
    new_width = image.width + border * 2
    new_height = image.height + border * 2
    base = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
    base.paste(image, (border, border))

    glow = base.convert("L").convert("RGBA")
    r, g, b, a = glow.split()
    r = r.point(lambda i: min(255, int(i * 3)))
    g = g.point(lambda i: min(255, int(i * 1.5)))
    b = b.point(lambda i: int(i * 0.1))
    glow_colored = Image.merge("RGBA", (r, g, b, a))

    glow_blurred = glow_colored.filter(ImageFilter.GaussianBlur(radius=30))
    result = Image.alpha_composite(glow_blurred, base)
    return result

@app.get("/outfit-image")
async def get_outfit(uid: str = Query(...), region: str = Query(...), key: str = Query(None)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    url = f"https://aditya-outfit-v6op.onrender.com/outfit-image?uid={uid}&region={region}"

    try:
        res = requests.get(url, timeout=20)

        if res.status_code != 200 or not res.headers.get("content-type", "").startswith("image"):
            # إذا الصورة ما جاتش، نصنع صورة فارغة مع تأثير التوهج
            blank = Image.new("RGBA", (512, 512), (0, 0, 0, 255))
            fire_img = create_fire_glow(blank, border=40)
        else:
            original = Image.open(BytesIO(res.content)).convert("RGBA")
            fire_img = create_fire_glow(original, border=40)

        font_size = max(40, int(fire_img.width * 0.1))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text_layer = Image.new("RGBA", fire_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        text = "@CH9AYFAX1"
        x, y = 20, 20

        # ظل النص
        shadow_color = (0, 0, 0, 180)
        draw.text((x + 3, y + 3), text, font=font, fill=shadow_color)

        # النص الأبيض
        text_color = (255, 255, 255, 220)
        draw.text((x, y), text, font=font, fill=text_color)

        final_img = Image.alpha_composite(fire_img, text_layer)

        output = BytesIO()
        final_img.save(output, format="PNG")
        output.seek(0)

        return Response(content=output.getvalue(), media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


