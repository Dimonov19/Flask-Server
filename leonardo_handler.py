import requests
import json
import os
import time
from config import LEONARDO_API_KEY

class LeonardoHandler:
    def __init__(self):
        self.api_key = LEONARDO_API_KEY
        self.base_url = "https://cloud.leonardo.ai/api/rest/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_image(self, prompt):
        try:
            # Создаём директорию для изображений, если её нет
            if not os.path.exists('images'):
                os.makedirs('images')

            # Отправляем запрос на генерацию изображения
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

            print(f"Статус запроса на генерацию: {response.status_code}")
            print(f"Ответ: {response.text}")

            if response.status_code != 200:
                print(f"Не удалось начать генерацию: {response.text}")
                return None

            # Получаем ID генерации
            generation_id = response.json().get("sdGenerationJob", {}).get("generationId")
            if not generation_id:
                print("Не получен ID генерации")
                return None

            # Ожидаем завершения генерации
            image_url = self._wait_for_generation(generation_id)
            if not image_url:
                return None

            # Скачиваем изображение
            image_path = "images/generated_image.png"
            image_response = requests.get(image_url)

            if image_response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                print(f"Изображение сохранено: {image_path}")
                return image_path
            else:
                print(f"Не удалось скачать изображение: {image_response.text}")
                return None

        except Exception as e:
            print(f"Ошибка в generate_image:")
            print(f"Тип исключения: {type(e)}")
            print(f"Сообщение исключения: {str(e)}")
            import traceback
            print(f"Трейсбек:\n{traceback.format_exc()}")
            return None

    def _wait_for_generation(self, generation_id):
        status_url = f"{self.base_url}/generations/{generation_id}"
        max_attempts = 30

        for attempt in range(max_attempts):
            try:
                print(f"\nПроверка статуса генерации (попытка {attempt + 1}/{max_attempts})")
                response = requests.get(status_url, headers=self.headers)
                print(f"Ответ на проверку статуса: {response.status_code}")
                print(f"Ответ: {response.text}")

                if response.status_code == 200:
                    data = response.json()
                    generations = data.get("generations_by_pk", {}).get("generated_images", [])

                    if generations and generations[0].get("url"):
                        image_url = generations[0]["url"]
                        print(f"\nURL изображения получен: {image_url}")
                        return image_url

                time.sleep(2)

            except Exception as e:
                print(f"Ошибка при проверке статуса генерации: {str(e)}")
                time.sleep(2)

        print("Время ожидания генерации истекло")
        return None
