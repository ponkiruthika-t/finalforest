import sys
import json
import os
from inference_sdk import InferenceHTTPClient, InferenceConfiguration

api_key = os.environ.get("ROBOFLOW_API_KEY")

if not api_key:
    print(json.dumps({
        "error": "ROBOFLOW_API_KEY is not set"
    }))
    sys.exit(1)

if len(sys.argv) < 2:
    print(json.dumps({
        "error": "No image path provided"
    }))
    sys.exit(1)

image_path = sys.argv[1]

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=api_key
).configure(
    InferenceConfiguration(
        api_key_transport="header"
    )
)

result = client.infer(
    image_path,
    model_id="wild-animal-xwqdm/4"
)

predictions = result.get("predictions", [])

detections = []

for prediction in predictions:
    detections.append({
        "label": prediction.get("class", "unknown"),
        "confidence": round(float(prediction.get("confidence", 0)), 4)
    })

print(json.dumps(detections))