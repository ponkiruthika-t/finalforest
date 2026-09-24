from flask import Flask, request, jsonify
from flask_cors import CORS
from inference_sdk import InferenceHTTPClient, InferenceConfiguration
import os
import tempfile

app = Flask(__name__)
CORS(app)

api_key = os.environ.get("ROBOFLOW_API_KEY")

if not api_key:
    raise RuntimeError("ROBOFLOW_API_KEY is not set")

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=api_key
).configure(
    InferenceConfiguration(
        api_key_transport="header"
    )
)

@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "message": "ForestGuard Python backend is running"
    })


@app.post("/api/detect")
def detect():
    if "image" not in request.files:
        return jsonify({
            "error": "No image received"
        }), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({
            "error": "No image selected"
        }), 400

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        ) as temp_file:

            image.save(temp_file.name)
            temp_path = temp_file.name

        result = client.infer(
            temp_path,
            model_id="wild-animal-xwqdm/4"
        )

        predictions = result.get("predictions", [])

        if not predictions:
            return jsonify({
                "label": "No threat",
                "raw_label": "No detection",
                "confidence": 0,
                "model": "Roboflow Wildlife Model",
                "zone": "Forest Zone A",
                "alert": False
            })

        predictions.sort(
            key=lambda x: float(x.get("confidence", 0)),
            reverse=True
        )

        best = predictions[0]

        detected_class = str(
            best.get("class", "unknown")
        ).lower()

        confidence = round(
            float(best.get("confidence", 0)),
            4
        )

        wild_animals = [
            "lion",
            "tiger",
            "leopard",
            "elephant",
            "bear",
            "deer",
            "wild boar",
            "boar",
            "wolf",
            "fox",
            "monkey",
            "zebra",
            "giraffe",
            "rhinoceros",
            "rhino",
            "crocodile"
        ]

        domestic_animals = [
            "dog",
            "cat",
            "cow",
            "horse",
            "sheep",
            "goat",
            "pig",
            "chicken"
        ]

        label = "Unknown"
        alert = False

        if detected_class in wild_animals:
            label = "Wild animal"
            alert = True

        elif detected_class in domestic_animals:
            label = "Domestic animal"
            alert = False

        elif detected_class in ["person", "human"]:
            label = "Human intrusion"
            alert = True

        return jsonify({
            "label": label,
            "raw_label": best.get("class", "unknown"),
            "confidence": confidence,
            "model": "Roboflow Wildlife Model",
            "zone": "Forest Zone A",
            "alert": alert
        })

    except Exception as error:
        return jsonify({
            "error": "Roboflow detection failed",
            "details": str(error)
        }), 500

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )