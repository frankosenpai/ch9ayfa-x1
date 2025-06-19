from fastapi import FastAPI, Query, HTTPException, Response
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO

app = FastAPI()

API_KEY = "ch9ayfa"

def create_fire_glow(image, border=40):
    # نزيد إطار شفاف حول الصورة لإضافة تأثير التوهج
    new_width = image.width + border * 2
    new_height = image.height + border * 2
    base = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
    base.paste(image, (border, border))

    # نحول الصورة إلى رمادي ثم نطبق تأثير الألوان الأحمر والبرتقالي
    glow = base.convert("L").convert("RGBA")
    r, g, b, a = glow.split()
    r = r.point(lambda i: min(255, int(i * 3)))  # زيادة الأحمر
    g = g.point(lambda i: min(255, int(i * 1.5)))  # زيادة البرتقالي
    b = b.point(lambda i: int(i * 0.1))  # تقليل الأزرق
    glow_colored = Image.merge("RGBA", (r, g, b, a))

    # نعمل Blur لتأثير التوهج
    glow_blurred = glow_colored.filter(ImageFilter.GaussianBlur(radius=30))
    result = Image.alpha_composite(glow_blurred, base)
    return result

@app.get("/outfit-image")
def get_outfit(uid: str = Query(...), region: str = Query(...), key: str = Query(None)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    url = f"https://aditya-outfit-v6op.onrender.com/outfit-image?uid={uid}&region={region}"

    try:
        res = requests.get(url, timeout=20)
        # تحقق من أن الاستجابة صورة
        if res.status_code != 200 or not res.headers.get("content-type", "").startswith("image"):
            raise HTTPException(status_code=400, detail="Image not found or invalid response")

        original = Image.open(BytesIO(res.content)).convert("RGBA")

        # إضافة تأثير النار حول الصورة
        fire_img = create_fire_glow(original, border=40)

        # تحديد حجم الخط بناءً على عرض الصورة (مثلاً 10% من عرض الصورة)
        font_size = max(40, int(fire_img.width * 0.1))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # إنشاء طبقة شفافة لنص العلامة
        text_layer = Image.new("RGBA", fire_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        text = "@CH9AYFAX1"

        # تحديد مكان النص (20 بكسل من الأعلى واليسار)
        x, y = 20, 20

        # رسم ظل للنص لزيادة وضوحه
        shadow_color = (0, 0, 0, 180)
        draw.text((x + 3, y + 3), text, font=font, fill=shadow_color)

        # رسم النص باللون الأبيض وبشفافية عالية قليلاً
        text_color = (255, 255, 255, 220)
        draw.text((x, y), text, font=font, fill=text_color)

        # دمج النص مع الصورة النهائية
        final_img = Image.alpha_composite(fire_img, text_layer)

        output = BytesIO()
        final_img.save(output, format="PNG")
        output.seek(0)

        return Response(content=output.getvalue(), media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

