const express = require("express");
const multer = require("multer");
const cors = require("cors");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

const uploadDir = path.join(__dirname, "uploads");

if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

// ===============================
// IMAGE UPLOAD
// ===============================

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, uploadDir);
    },

    filename: function (req, file, cb) {
        const ext = path.extname(file.originalname).toLowerCase() || ".jpg";
        const filename = `${Date.now()}${ext}`;
        cb(null, filename);
    }
});

const upload = multer({
    storage: storage
});

// ===============================
// MODEL STATUS
// ===============================

app.get("/api/yolo-status", (req, res) => {
    res.json({
        online: true,
        model: "Roboflow Wildlife Model",
        model_id: "wild-animal-xwqdm/4"
    });
});

// ===============================
// IMAGE DETECTION
// ===============================

app.post("/api/detect", upload.single("image"), (req, res) => {

    if (!req.file) {
        return res.status(400).json({
            error: "No image received"
        });
    }

    const imagePath = req.file.path;

    console.log("Image received:", imagePath);

    const python = spawn(
        "python",
        [
            path.join(__dirname, "roboflow_detect.py"),
            imagePath
        ],
        {
            cwd: __dirname
        }
    );

    let output = "";
    let errorOutput = "";

    python.stdout.on("data", (data) => {
        output += data.toString();
    });

    python.stderr.on("data", (data) => {
        errorOutput += data.toString();
    });

    python.on("close", (code) => {

        console.log("Roboflow exit code:", code);

        if (errorOutput) {
            console.log("Roboflow error:", errorOutput);
        }

        if (output) {
            console.log("Roboflow output:", output);
        }

        // Delete uploaded image after processing
        try {
            fs.unlinkSync(imagePath);
        } catch (e) {
            console.log("Could not delete uploaded image.");
        }

        if (code !== 0) {
            return res.status(500).json({
                error: "Roboflow detection failed",
                details: errorOutput || output || "Unknown Python error"
            });
        }

        try {

            const detections = JSON.parse(output.trim());

            // Nothing detected
            if (!detections.length) {

                return res.json({
                    label: "No threat",
                    raw_label: "No detection",
                    confidence: 0,
                    model: "Roboflow Wildlife Model",
                    zone: "Forest Zone A",
                    alert: false
                });
            }

            // Highest confidence detection
            detections.sort(
                (a, b) => b.confidence - a.confidence
            );

            const best = detections[0];

            const detectedClass = best.label.toLowerCase();

            // Wildlife classes
            const wildAnimals = [
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
            ];

            // Domestic classes
            const domesticAnimals = [
                "dog",
                "cat",
                "cow",
                "horse",
                "sheep",
                "goat",
                "pig",
                "chicken"
            ];

            let label = "No threat";
            let alert = false;

            if (wildAnimals.includes(detectedClass)) {

                label = "Wild animal";
                alert = true;

            } else if (domesticAnimals.includes(detectedClass)) {

                label = "Domestic animal";
                alert = false;

            } else if (detectedClass === "person" ||
                       detectedClass === "human") {

                label = "Human intrusion";
                alert = true;

            } else {

                label = "Unknown";
                alert = false;
            }

            res.json({
                label: label,
                raw_label: best.label,
                confidence: best.confidence,
                model: "Roboflow Wildlife Model",
                zone: "Forest Zone A",
                alert: alert
            });

        } catch (err) {

            console.error("JSON parsing error:", err);
            console.error("Roboflow output:", output);

            return res.status(500).json({
                error: "Invalid Roboflow response",
                details: err.message
            });
        }
    });
});

// ===============================
// START SERVER
// ===============================

app.listen(PORT, () => {
    console.log(
        `ForestGuard server running at http://localhost:${PORT}`
    );
});