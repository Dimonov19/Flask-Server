from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from datetime import datetime
import webuiapi
import base64
from PIL import Image
import io
import requests  # Для загрузки изображений по URL
from io import BytesIO

app = FastAPI()

os.makedirs("public_images", exist_ok=True)
app.mount("/images", StaticFiles(directory="public_images"), name="images")

class ImageRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_image(request: Request, data: ImageRequest):
    try:
        api = webuiapi.WebUIApi()

        result = api.txt2img(
            prompt=data.prompt,
            negative_prompt="",
            seed=-1,
            steps=20,
            cfg_scale=7.0,
            width=512,
            height=512,
            sampler_name="Euler a"
        )

        # Сохраняем изображение в память
        img_byte_arr = io.BytesIO()
        result.image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Конвертируем в base64
        base64_image = base64.b64encode(img_byte_arr).decode('utf-8')

        # Сохраняем файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.png"
        image_path = os.path.join("public_images", filename)
        result.image.save(image_path)

        base_url = str(request.base_url)
        if "ngrok" in request.headers.get("host", ""):
            base_url = f"https://{request.headers.get('host')}/"

        image_url = f"{base_url}images/{filename}"

        return {
            "success": True, 
            "image_url": image_url,
            "image_data": base64_image
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.post("/convert-url-to-base64")
async def convert_url_to_base64(request: Request):
    try:
        body = await request.json()
        image_url = body.get("image_url")

        if not image_url:
            return JSONResponse(content={"success": False, "error": "No image URL provided"}, status_code=400)

        # Загрузка изображения по URL
        response = requests.get(image_url)
        if response.status_code != 200:
            return JSONResponse(content={"success": False, "error": "Failed to download image"}, status_code=500)

        # Конвертация изображения в Base64
        image = Image.open(BytesIO(response.content))
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        b64_string = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return {"success": True, "image_data": b64_string}

    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)