from flask import Flask, request, jsonify, send_file
import requests
import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip
from werkzeug.utils import secure_filename

app = Flask(__name__)
os.makedirs("downloads", exist_ok=True)

@app.route("/")
def index():
    return "Luxury Bot is live!"

@app.route("/combine", methods=["POST"])
def combine():
    try:
        data = request.json
        video_url = data.get("video_url")
        audio_url = data.get("audio_url")

        if not video_url or not audio_url:
            return jsonify({"error": "Missing video_url or audio_url"}), 400

        video_path = os.path.join("downloads", "temp_video.mp4")
        audio_path = os.path.join("downloads", "temp_audio.mp3")
        output_path = os.path.join("downloads", "final_video.mp4")

        # Last ned video
        video_data = requests.get(video_url)
        with open(video_path, "wb") as f:
            f.write(video_data.content)

        # Last ned lyd
        audio_data = requests.get(audio_url)
        with open(audio_path, "wb") as f:
            f.write(audio_data.content)

        # Konverter MP3 til WAV (fix for MoviePy)
        wav_path = os.path.join("downloads", "temp_audio.wav")
        AudioSegment.from_file(audio_path).export(wav_path, format="wav")

        # Kombiner video + lyd
        video = VideoFileClip(video_path)
        audio = AudioFileClip(wav_path)
        final = video.set_audio(audio)
        final.write_videofile(output_path, codec="libx264", audio_codec="aac")

        return send_file(output_path, mimetype="video/mp4")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

