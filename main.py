from flask import Flask, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Luxury Bot is running successfully!",
        "status": "✅",
        "developer": "Vincent"
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), debug=True)
