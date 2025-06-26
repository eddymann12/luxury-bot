from flask import Flask, request, send_file, jsonify
import requests
import os
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment

app = Flask(__name__)

@app.route("/combine", methods=["POST"])
def combine_video_and_audio():
    data = request.json
    video_url = data.get("video_url")
    audio_url = data.get("audio_url")

    if not video_url or not audio_url:
        return jsonify({"error": "Missing video_url or audio_url"}), 400

    try:
        os.makedirs("downloads", exist_ok=True)

        video_path = "downloads/temp_video.mp4"
        audio_mp3_path = "downloads/temp_audio.mp3"
        audio_wav_path = "downloads/temp_audio.wav"
        output_path = "downloads/final_output.mp4"

        with open(video_path, "wb") as f:
            f.write(requests.get(video_url).content)

        with open(audio_mp3_path, "wb") as f:
            f.write(requests.get(audio_url).content)

        # Konverter MP3 til WAV (MoviePy leser WAV mer stabilt)
        audio = AudioSegment.from_mp3(audio_mp3_path)
        audio.export(audio_wav_path, format="wav")

        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_wav_path).set_duration(video_clip.duration)

        final = video_clip.set_audio(audio_clip)
        final.write_videofile(output_path, codec="libx264", audio_codec="aac")

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
