rom flask import Flask, jsonify, request
import requests
import os
import random

app = Flask(__name__)

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_BASE_URL = "https://api.pexels.com/videos/search"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CAPCUT_WEBHOOK_URL = os.getenv("CAPCUT_WEBHOOK_URL")  # Webhook endpoint for CapCut

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

    videos = response.json().get("videos", [])
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

@app.route("/quote")
def get_quote():
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "Du er en tekstforfatter som lager korte, kraftige luksus-livsstils quotes."},
            {"role": "user", "content": "Lag én kort quote om luksus, suksess eller ambisjon."}
        ],
        "max_tokens": 50
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Failed to generate quote", "status_code": response.status_code}), 500
    result = response.json()
    quote = result['choices'][0]['message']['content'].strip()
    return jsonify({"quote": quote})

@app.route("/create-video")
def create_video():
    # Hent video og quote
    video_res = get_luxury_video()
    if video_res.status_code != 200:
        return video_res

    quote_res = get_quote()
    if quote_res.status_code != 200:
        return quote_res

    video_url = video_res.json()["video_url"]
    quote = quote_res.json()["quote"]

    payload = {
        "video_url": video_url,
        "quote": quote
    }
    try:
        capcut_response = requests.post(CAPCUT_WEBHOOK_URL, json=payload)
        if capcut_response.status_code == 200:
            return jsonify({"message": "Video sent to CapCut successfully", "capcut_response": capcut_response.json()})
        else:
            return jsonify({"error": "CapCut failed", "status_code": capcut_response.status_code, "details": capcut_response.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
