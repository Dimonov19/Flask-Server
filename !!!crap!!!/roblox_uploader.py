import requests
import json
import time
from config import ROBLOX_API_KEY, ROBLOX_USER_ID

class RobloxUploader:
    def __init__(self):
        self.api_key = ROBLOX_API_KEY
        self.base_url = "https://apis.roblox.com"
        self.user_id = ROBLOX_USER_ID

    def _get_creator_hub_image_id(self, decal_id):
        """Получаем ID изображения через Creator Hub API"""
        headers = {
            'x-api-key': self.api_key,
            'Accept': 'application/json'
        }

        try:
            # Запрашиваем информацию о связанных ассетах из Creator Hub
            url = f"{self.base_url}/creator-hub/v1/assets/details"
            params = {
                'assetId': decal_id
            }
            
            print(f"\nRequesting Creator Hub details for decal: {decal_id}")
            response = requests.get(url, headers=headers, params=params)
            print(f"Creator Hub response: {response.status_code}")
            print(f"Response content: {response.text}")

            if response.status_code == 200:
                data = response.json()
                # Проверяем различные возможные поля в ответе
                image_id = data.get('sourceAssetId') or data.get('imageAssetId')
                if image_id:
                    return str(image_id)

            # Альтернативный эндпоинт
            url = f"{self.base_url}/creator-hub/v1/marketplace/assets/{decal_id}"
            print(f"\nTrying marketplace endpoint")
            response = requests.get(url, headers=headers)
            print(f"Marketplace response: {response.status_code}")
            print(f"Response content: {response.text}")

            if response.status_code == 200:
                data = response.json()
                image_id = data.get('sourceAssetId') or data.get('imageAssetId')
                if image_id:
                    return str(image_id)

        except Exception as e:
            print(f"Error getting Creator Hub details: {str(e)}")
        return None

    def upload_image(self, image_path):
        try:
            print(f"Starting image upload: {image_path}")
            
            request_data = {
                "assetType": "Decal",
                "displayName": "Generated Image",
                "description": "Generated using AI",
                "creationContext": {"creator": {"userId": self.user_id}}
            }
            
            headers = {'x-api-key': self.api_key}
            
            with open(image_path, 'rb') as image_file:
                files = {
                    'request': (None, json.dumps(request_data), 'application/json'),
                    'fileContent': ('image.png', image_file, 'image/png')
                }
                
                print("Sending upload request...")
                response = requests.post(
                    f"{self.base_url}/assets/v1/assets", 
                    headers=headers, 
                    files=files
                )
                
                print(f"Upload response status: {response.status_code}")
                print(f"Upload response content: {response.text}")
                
                if response.status_code == 200:
                    operation_id = response.json().get('operationId')
                    if not operation_id:
                        return {"success": False, "error": "No operation ID received"}
                    
                    # Ждем завершения операции и пытаемся получить ID
                    for attempt in range(10):
                        print(f"Checking operation status (attempt {attempt + 1}/10)")
                        
                        status_response = requests.get(
                            f"{self.base_url}/assets/v1/operations/{operation_id}",
                            headers=headers
                        )
                        
                        if status_response.status_code == 200:
                            data = status_response.json()
                            if data.get('done'):
                                decal_id = data.get('response', {}).get('assetId')
                                if decal_id:
                                    # Небольшая пауза перед запросом Creator Hub
                                    time.sleep(2)
                                    # Получаем image_id через Creator Hub
                                    image_id = self._get_creator_hub_image_id(decal_id)
                                    print(f"Success! Decal ID: {decal_id}, Image ID: {image_id}")
                                    return {
                                        "success": True,
                                        "decal_id": decal_id,
                                        "image_id": image_id or decal_id
                                    }
                        time.sleep(2)
                    
                    return {"success": False, "error": "Operation timed out"}
                
                return {"success": False, "error": f"Upload failed: {response.text}"}
                
        except Exception as e:
            print(f"Error in upload_image: {str(e)}")
            return {"success": False, "error": str(e)}