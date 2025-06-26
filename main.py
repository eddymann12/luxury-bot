from flask import Flask, jsonify, request
import requests
import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip
from datetime import datetime
from pydub import AudioSegment

app = Flask(__name__)

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_BASE_URL = "https://api.pexels.com/videos/search"
UPLOAD_FOLDER = "downloads"

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

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Optional: manually set ffmpeg path for pydub
AudioSegment.converter = "/usr/bin/ffmpeg"

@app.route("/")
def index():
    return jsonify({
        "developer": "Vincent",
        "message": "Luxury Bot is running successfully!",
        "status": "✅"
    })

@app.route("/luxury-video")
def get_luxury_video():
    headers = {"Authorization": PEXELS_API_KEY}
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

@app.route("/generate-video")
def generate_video():
    video_url = request.args.get("video_url")
    audio_url = request.args.get("audio_url")

    if not video_url or not audio_url:
        return jsonify({"error": "Missing video_url or audio_url"}), 400

    try:
        video_path = os.path.join(UPLOAD_FOLDER, "temp_video.mp4")
        audio_path = os.path.join(UPLOAD_FOLDER, "temp_audio.mp3")
        wav_audio_path = os.path.join(UPLOAD_FOLDER, "temp_audio.wav")
        output_path = os.path.join(UPLOAD_FOLDER, f"final_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4")

        with open(video_path, "wb") as v:
            v.write(requests.get(video_url).content)
        with open(audio_path, "wb") as a:
            a.write(requests.get(audio_url).content)

        # Convert MP3 to WAV
        mp3_audio = AudioSegment.from_mp3(audio_path)
        mp3_audio.export(wav_audio_path, format="wav")

        video = VideoFileClip(video_path).subclip(0, 14)
        audio = AudioFileClip(wav_audio_path)
        final = video.set_audio(audio)
        final.write_videofile(output_path, codec="libx264", audio_codec="aac")

        return jsonify({"result": "Video generated", "output_file": output_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
