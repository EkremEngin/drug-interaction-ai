from flask import Flask, request, jsonify
from predictor import predict_interactions
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Metin bulunamadı"}), 400

    text = data["text"]
    style_raw = data.get("style", 1)

    try:
        style = int(style_raw)
    except (ValueError, TypeError):
        style = 1

    if style not in (1, 2, 3, 4):
        style = 1

    result = predict_interactions(text, style)
    return jsonify(result), 200


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
