import requests
import json
import os
import time
from config import LEONARDO_API_KEY

class LeonardoHandler:  # Здесь была ошибка - класс назывался LeonardoHandler, а не LeonardoAI
    def __init__(self):
        self.api_key = LEONARDO_API_KEY
        self.base_url = "https://cloud.leonardo.ai/api/rest/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_image(self, prompt):
        try:
            # Создаем директорию для изображений, если её нет
            if not os.path.exists('images'):
                os.makedirs('images')

            # Отправляем запрос на генерацию
            generation_url = f"{self.base_url}/generations"
            generation_data = {
                "prompt": prompt,
                "modelId": "ac614f96-1082-45bf-be9d-757f2d31c174",  # DreamShaper v7
                "width": 512,
                "height": 512,
                "promptMagic": False,
                "public": False
            }

            response = requests.post(
                generation_url,
                headers=self.headers,
                json=generation_data
            )

            print(f"Generation request status: {response.status_code}")
            print(f"Response content: {response.text}")

            if response.status_code != 200:
                print(f"Failed to start generation: {response.text}")
                return None

            generation_id = response.json()["sdGenerationJob"]["generationId"]

            # Ждем завершения генерации
            image_url = self._wait_for_generation(generation_id)
            if not image_url:
                return None

            # Сохраняем изображение
            image_path = "images/generated_image.png"
            image_response = requests.get(image_url)

            if image_response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                print(f"\nImage saved to: {image_path}")
                return image_path
            else:
                print(f"Failed to download image: {image_response.text}")
                return None

        except Exception as e:
            print(f"Error in generate_image:")
            print(f"Exception type: {type(e)}")
            print(f"Exception message: {str(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            return None

    def _wait_for_generation(self, generation_id):
        status_url = f"{self.base_url}/generations/{generation_id}"
        max_attempts = 30

        for attempt in range(max_attempts):
            try:
                print(f"\nChecking generation status (attempt {attempt + 1}/{max_attempts})")
                response = requests.get(status_url, headers=self.headers)
                print(f"Status check response: {response.status_code}")
                print(f"Response content: {response.text}")

                if response.status_code == 200:
                    data = response.json()
                    generations = data.get("generations_by_pk", {}).get("generated_images", [])

                    if generations and generations[0].get("url"):
                        image_url = generations[0]["url"]
                        print(f"\nImage URL received: {image_url}")
                        return image_url

                time.sleep(2)

            except Exception as e:
                print(f"Error checking generation status: {str(e)}")
                time.sleep(2)

        print("Generation timed out")
        return None