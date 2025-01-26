import requests
import json
import time
from config import ROBLOX_API_KEY, ROBLOX_USER_ID

class RobloxUploader:
    def __init__(self):
        self.api_key = ROBLOX_API_KEY
        self.base_url = "https://apis.roblox.com"
        self.user_id = ROBLOX_USER_ID

    def _get_image_id_from_decal(self, decal_id):
        """Получает Image ID из Decal, используя Studio API"""
        headers = {
            'x-api-key': self.api_key,
            'Accept': 'application/json'
        }

        # Попытка 1: Используем Studio Asset Info API
        try:
            url = f"{self.base_url}/asset-types-api/v1/asset/{decal_id}"
            response = requests.get(url, headers=headers)
            print(f"Studio Asset Info response: {response.status_code}")
            print(f"Response content: {response.text}")

            if response.status_code == 200:
                data = response.json()
                return data.get('sourceAssetId')
        except Exception as e:
            print(f"Error in Studio Asset Info: {str(e)}")

        # Попытка 2: Используем Metadata API
        try:
            url = f"{self.base_url}/universes/v1/assets/{decal_id}/metadata"
            response = requests.get(url, headers=headers)
            print(f"Metadata API response: {response.status_code}")
            print(f"Response content: {response.text}")

            if response.status_code == 200:
                data = response.json()
                return data.get('imageId') or data.get('sourceImageId')
        except Exception as e:
            print(f"Error in Metadata API: {str(e)}")

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
                
                upload_url = f"{self.base_url}/assets/v1/assets"
                print("Sending upload request...")
                response = requests.post(upload_url, headers=headers, files=files)
                print(f"Upload response status: {response.status_code}")
                print(f"Upload response content: {response.text}")
                
                if response.status_code == 200:
                    operation_id = response.json().get('operationId')
                    if not operation_id:
                        return {"success": False, "error": "No operation ID received"}
                    
                    print(f"Got operation ID: {operation_id}")
                    
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
                                    image_id = self._get_image_id_from_decal(decal_id)
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