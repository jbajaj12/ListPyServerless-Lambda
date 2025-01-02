import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    # Use jsonify for JSON responses
    return jsonify(msg="Hello world!")

if __name__ == "__main__":
    # Set host and port, fallback to 8080 if PORT is not set
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
