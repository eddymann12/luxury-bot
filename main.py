from flask import Flask, request, jsonify
import os
import requests
from moviepy.editor import VideoFileClip, AudioFileClip
from datetime import datetime

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/")
def home():
    return "Luxury Bot is live!"

@app.route("/combine", methods=["POST"])
def combine():
    data = request.get_json()
    video_url = data.get("video_url")
    audio_url = data.get("audio_url")

    if not video_url or not audio_url:
        return jsonify({"error": "Missing video_url or audio_url"}), 400

    try:
        video_path = os.path.join(DOWNLOAD_FOLDER, f"video_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4")
        audio_path = os.path.join(DOWNLOAD_FOLDER, f"audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3")
        output_path = os.path.join(DOWNLOAD_FOLDER, f"final_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4")

        with open(video_path, "wb") as f:
            f.write(requests.get(video_url).content)

        with open(audio_path, "wb") as f:
            f.write(requests.get(audio_url).content)

        video = VideoFileClip(video_path).subclip(0, 14)
        audio = AudioFileClip(audio_path)
        final = video.set_audio(audio)
        final.write_videofile(output_path, codec="libx264", audio_codec="aac")

        return jsonify({"message": "Video created", "file_path": output_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
