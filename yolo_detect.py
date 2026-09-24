import sys
import json
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

image_path = sys.argv[1]

results = model.predict(
    source=image_path,
    conf=0.35,
    verbose=False
)

wild_animals = {
    "elephant",
    "bear",
    "zebra",
    "giraffe"
}

domestic_animals = {
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow"
}

detections = []

for result in results:
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = result.names[class_id].lower()

        if class_name in wild_animals:
            animal_type = "Wild Animal"
            alert = True

        elif class_name in domestic_animals:
            animal_type = "Domestic Animal"
            alert = False

        elif class_name == "person":
            animal_type = "Human"
            alert = True

        else:
            animal_type = "Unknown"
            alert = False

        detections.append({
            "label": class_name,
            "confidence": round(confidence, 4),
            "type": animal_type,
            "alert": alert
        })

print(json.dumps(detections))