from flask import Flask, request, jsonify
from flask_cors import CORS
from leonardo_handler import LeonardoHandler
from roblox_uploader import RobloxUploader
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        print(f"Prompt received in Flask server: {prompt}")

        # Генерация изображения через Leonardo AI
        leonardo = LeonardoHandler()
        image_path = leonardo.generate_image(prompt)

        if not image_path:
            return jsonify({"success": False, "error": "Failed to generate image"}), 400

        print(f"Generated image path: {image_path}")

        # Загрузка изображения в Roblox
        roblox = RobloxUploader()
        result = roblox.upload_image(image_path)

        if not result.get("success"):
            print(f"Upload failed: {result.get('error')}")
            return jsonify({"success": False, "error": result.get('error')}), 400

        print(f"Roblox upload result: {result}")

        return jsonify({
            "success": True,
            "decal_id": result.get("decal_id"),
            "image_id": result.get("image_id")
        })

    except Exception as e:
        print(f"Error in generate endpoint: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)