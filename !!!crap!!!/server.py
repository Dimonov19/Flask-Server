from flask import Flask, request, jsonify
import os
from leonardo_handler import LeonardoHandler

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({"success": False, "error": "Prompt is required"}), 400

        result = LeonardoHandler.generate_image(prompt)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)