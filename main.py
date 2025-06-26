from flask import Flask, jsonify
import requests
import os
import random

app = Flask(__name__)

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_BASE_URL = "https://api.pexels.com/videos/search"

luxury_keywords = [
    "celebrity lifestyle",
    "private jet",
    "supercar",
    "luxury yacht",
    "penthouse",
    "bugatti",
    "rolex",
    "luxury mansion",
    "luxury life",
    "rich people"
]

@app.route("/")
def index():
    return jsonify({
        "developer": "Vincent",
        "message": "Luxury Bot is running successfully!",
        "status": "✅"
    })

@app.route("/luxury-video")
def get_luxury_video():
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": random.choice(luxury_keywords),
        "orientation": "portrait",
        "per_page": 15  # Økt antall resultater
    }

    response = requests.get(PEXELS_BASE_URL, headers=headers, params=params)

    if response.status_code != 200:
        return jsonify({
            "error": "Failed to fetch videos from Pexels",
            "status_code": response.status_code
        }), 500

    data = response.json()
    videos = data.get("videos", [])

    if not videos:
        return jsonify({"error": "No videos found"}), 404

    # Finn beste (1080x1920)
    best_quality = None
    for video in videos:
        for file in video.get("video_files", []):
            if file["width"] == 1080 and file["height"] == 1920:
                best_quality = file["link"]
                break
        if best_quality:
            break

    # Fallback hvis ingen 1080x1920
    if not best_quality:
        for video in videos:
            for file in video.get("video_files", []):
                if file.get("link"):
                    best_quality = file["link"]
                    break
            if best_quality:
                break

    if not best_quality:
        return jsonify({"error": "No suitable video found"}), 404

    return jsonify({"video_url": best_quality})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
