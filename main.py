from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Luxury Video Bot is live and ready!"

if __name__ == "__main__":
import os
app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), debug=True)

