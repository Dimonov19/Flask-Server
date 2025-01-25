import requests
import json

def test_image_generation():
    url = "http://localhost:5001/generate"  # Изменено с 5000 на 5001
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "prompt": "cat"
    }

    print(f"Sending request to: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print("\nGeneration successful!")
            print(f"Decal ID: {result.get('decal_id')}")
            print(f"Image ID: {result.get('image_id')}")
        else:
            print(f"\nError: {response.text}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    test_image_generation()