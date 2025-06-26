from flask import Flask, jsonify, request
import requests
import os
import random
import urllib.request

app = Flask(__name__)

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
UPLOADCARE_PUBLIC_KEY = os.getenv("UPLOADCARE_PUBLIC_KEY")
UPLOADCARE_SECRET_KEY = os.getenv("UPLOADCARE_SECRET_KEY")
PEXELS_BASE_URL = "https://api.pexels.com/videos/search"
UPLOADCARE_UPLOAD_URL = "https://upload.uploadcare.com/base/"

luxury_keywords = [
    "celebrity lifestyle",
    "private jet",
    "supercar",
    "luxury yacht",
    "penthouse",
    "bugatti",
    "rolex",
    "luxury mansion"
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
        "per_page": 5
    }

    response = requests.get(PEXELS_BASE_URL, headers=headers, params=params)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch videos from Pexels", "status_code": response.status_code}), 500

    data = response.json()
    videos = data.get("videos", [])

    best_quality = None
    for video in videos:
        for file in video.get("video_files", []):
            if file["width"] == 1080 and file["height"] == 1920:
                best_quality = file["link"]
                break
        if best_quality:
            break

    if not best_quality:
        return jsonify({"error": "No suitable 1080x1920 video found"}), 404

    return jsonify({"video_url": best_quality})

@app.route("/download-video")
def download_and_upload():
    try:
        video_resp = get_luxury_video().json
        video_url = video_resp.get("video_url")
        if not video_url:
            return jsonify({"error": "No video to download"}), 400

        local_filename = "/tmp/luxury.mp4"
        urllib.request.urlretrieve(video_url, local_filename)

        with open(local_filename, "rb") as f:
            upload_resp = requests.post(
                UPLOADCARE_UPLOAD_URL,
                files={"file": f},
                data={"UPLOADCARE_STORE": "1", "public_key": UPLOADCARE_PUBLIC_KEY}
            )

        if upload_resp.status_code == 200:
            upload_url = upload_resp.json().get("file")
            return jsonify({"uploadcare_url": f"https://ucarecdn.com/{upload_url}/"})
        else:
            return jsonify({"error": "Upload failed", "details": upload_resp.text}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
