from flask import Flask, request, jsonify, send_file
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
import os
import requests

app = Flask(__name__)

# Sørg for at nedlastingsmappen finnes
os.makedirs("downloads", exist_ok=True)

@app.route("/")
def home():
    return "🎬 Video generator is live!"

@app.route("/generate-video", methods=["GET"])
def generate_video():
    video_url = request.args.get("video_url")
    audio_url = request.args.get("audio_url")

    if not video_url or not audio_url:
        return jsonify({"error": "Missing 'video_url' or 'audio_url' parameter"}), 400

    try:
        # Last ned video
        video_path = "downloads/temp_video.mp4"
        with open(video_path, "wb") as f:
            f.write(requests.get(video_url).content)

        # Last ned MP3
        audio_mp3_path = "downloads/temp_audio.mp3"
        with open(audio_mp3_path, "wb") as f:
            f.write(requests.get(audio_url).content)

        # Konverter MP3 til WAV
        audio_wav_path = "downloads/temp_audio.wav"
        sound = AudioSegment.from_mp3(audio_mp3_path)
        sound.export(audio_wav_path, format="wav")

        # Sett sammen video og lyd
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_wav_path)
        final_video = video.set_audio(audio)

        output_path = "downloads/output.mp4"
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

