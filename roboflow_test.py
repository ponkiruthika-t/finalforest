import os
from inference_sdk import InferenceHTTPClient, InferenceConfiguration

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

result = client.infer(
    "uploads/myphoto.jpg",
    model_id="wild-animal-xwqdm/4"
)

print(result)