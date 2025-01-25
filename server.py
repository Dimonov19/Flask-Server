from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from leonardo_handler import LeonardoHandler
import os

app = FastAPI()

class ImageRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_image(request: Request, data: ImageRequest):
    try:
        result = LeonardoHandler.generate_image(data.prompt)
        if not result["success"]:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": result["error"]}
            )

        return {"success": True, "image_url": result["image_url"]}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
