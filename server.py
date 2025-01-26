from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from datetime import datetime
from leonardo_handler import LeonardoHandler  # Убедись, что этот модуль правильно подключен

# Создаем приложение FastAPI
app = FastAPI()

# Директория для публичных изображений
os.makedirs("public_images", exist_ok=True)
app.mount("/images", StaticFiles(directory="public_images"), name="images")


# Модель для запросов
class ImageRequest(BaseModel):
    prompt: str


# Эндпоинт для генерации изображения
@app.post("/generate")
async def generate_image(request: Request, data: ImageRequest):
    try:
        # Генерация изображения через LeonardoHandler
        response = LeonardoHandler.generate_image(data.prompt)
        if not response["success"]:
            raise Exception(response["error"])

        # Сохранение изображения
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.png"
        image_url = response["image_url"]

        # Сохранение ссылки на изображение
        base_url = str(request.base_url)
        if "ngrok" in request.headers.get("host", ""):
            base_url = f"https://{request.headers.get('host')}/"
        full_image_url = f"{base_url}images/{filename}"

        # Загружаем изображение с URL и сохраняем в папку
        image_response = requests.get(image_url)
        with open(os.path.join("public_images", filename), "wb") as f:
            f.write(image_response.content)

        return {
            "success": True,
            "image_url": full_image_url
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# Тестовый эндпоинт
@app.get("/")
async def root():
    return {"message": "Server is running!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
