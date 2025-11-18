from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.getenv("API_KEY"))

# Load Gemini model
model = genai.GenerativeModel("models/gemini-2.5-pro")


@app.route('/')
def home():
    return "✅ AI Authenticity Backend Running!"


@app.route('/analyze', methods=['POST'])
def analyze_product():
    try:
        link = request.form.get("product_link")
        image = request.files.get("image")

        # --- Unified JSON Output Prompt ---
        base_prompt = """
You are an AI Product Authenticity Evaluator.

Your task is to analyze whether a product (via image or link) appears original, fake, or unclear.

Return the final result ONLY in this exact JSON format:

{
  "originality_score": <0-100>,
  "brand_match": "Yes" or "No",
  "packaging_score": <0-100>,
  "verdict": "Original" or "Possibly Fake" or "Unclear"
}

Rules:
- ABSOLUTELY NO extra text or explanation outside the JSON.
- If details are insufficient → use scores 40–60 and verdict = "Unclear".
"""


        # If image uploaded
        if image:
            img_bytes = image.read()
            prompt = base_prompt + "\nNow evaluate the uploaded product image."
            response = model.generate_content(
                [prompt, {"mime_type": "image/jpeg", "data": img_bytes}]
            )

        # If product link provided
        elif link:
            prompt = base_prompt + f"\nNow evaluate this product link:\n{link}"
            response = model.generate_content(prompt)

        else:
            return jsonify({"error": "No link or image provided"}), 400

        # Return AI output directly
        return jsonify({"verdict": response.text.strip()})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
