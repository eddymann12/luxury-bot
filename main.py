from flask import Flask, request, jsonify
from moviepy.editor import VideoFileClip, AudioFileClip
import os
import requests
from datetime import datetime

app = Flask(__name__)
UPLOAD_DIR = "downloads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.route("/")
def index():
    return "Luxury Bot is live!"

@app.route("/combine", methods=["GET"])
def combine_video_audio():
    video_url = request.args.get("video_url")
    audio_url = request.args.get("audio_url")

    if not video_url or not audio_url:
        return jsonify({"error": "Missing video_url or audio_url"}), 400

    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        video_path = os.path.join(UPLOAD_DIR, f"video_{timestamp}.mp4")
        audio_path = os.path.join(UPLOAD_DIR, f"audio_{timestamp}.mp3")
        output_path = os.path.join(UPLOAD_DIR, f"final_{timestamp}.mp4")

        # Last ned video og lyd
        with open(video_path, "wb") as f:
            f.write(requests.get(video_url).content)
        with open(audio_path, "wb") as f:
            f.write(requests.get(audio_url).content)

        # Klipp og kombiner
        video_clip = VideoFileClip(video_path).subclip(0, 14)
        audio_clip = AudioFileClip(audio_path)
        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

        return jsonify({
            "message": "Video generated successfully",
            "output_file": output_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
