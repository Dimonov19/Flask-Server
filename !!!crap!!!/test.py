from leonardo_handler import LeonardoHandler

if __name__ == "__main__":
    prompt = input("Введите запрос: ")
    result = LeonardoHandler.generate_image(prompt)
    if result["success"]:
        print("Image URL:", result["image_url"])
    else:
        print("Error:", result["error"])
