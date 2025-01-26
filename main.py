import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from leonardo_handler import LeonardoHandler
from roblox_uploader import RobloxUploader
import traceback

app = Flask(__name__)
CORS(app)

# Получаем порт из переменной окружения, если не задан — используем 5001
port = int(os.environ.get("PORT", 5001))

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        # Генерация изображения через Leonardo AI
        leonardo = LeonardoHandler()
        image_path = leonardo.generate_image(prompt)

        if not image_path:
            return jsonify({"success": False, "error": "Failed to generate image"}), 400

        # Загрузка в Roblox
        roblox = RobloxUploader()
        result = roblox.upload_image(image_path)

        if not result.get("success"):
            print(f"Upload failed: {result.get('error')}")
            return jsonify({"success": False, "error": result.get('error')}), 400

        return jsonify({
            "success": True,
            "decal_id": result.get("decal_id"),
            "image_id": result.get("image_id")
        })

    except Exception as e:
        print(f"Error in generate endpoint:")
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)