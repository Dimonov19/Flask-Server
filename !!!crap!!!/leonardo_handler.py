import requests

class LeonardoHandler:
    API_URL = "https://cloud.leonardo.ai/api/rest/v1/generations"
    API_KEY = "77c5479d-5db4-4930-a42b-977bb755c152"  # Ваш ключ Leonardo AI

    @staticmethod
    def generate_image(prompt: str):
        try:
            response = requests.post(
                LeonardoHandler.API_URL,
                headers={"Authorization": f"Bearer {LeonardoHandler.API_KEY}"},
                json={
                    "prompt": prompt,
                    "negative_prompt": "",
                    "modelId": "ac614f96-1082-45bf-be9d-757f2d31c174",
                    "scheduler": "EULER_DISCRETE"
                }
            )
            response_data = response.json()

            if response.status_code != 200:
                raise Exception(f"Leonardo API error: {response.text}")

            generated_images = response_data.get("generated_images", [])
            if not generated_images:
                raise Exception("No images generated by Leonardo API")

            image_url = generated_images[0]["url"]
            return {"success": True, "image_url": image_url}
        except Exception as e:
            return {"success": False, "error": str(e)}