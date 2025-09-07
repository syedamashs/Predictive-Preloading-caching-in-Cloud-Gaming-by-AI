from flask import Flask, request, jsonify, send_file, render_template
import os
import json

app = Flask(__name__)

CACHE_FILE = "cache.json"
VIDEO_DIR = "videos"

# ------------------------
# Load or create cache
# ------------------------
if not os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "w") as f:
        json.dump([], f)

def load_cache():
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ------------------------
# Single Endpoint
# ------------------------
@app.route("/game", methods=["POST"])
def game():
    data = request.get_json()
    userId = data.get("userId")
    numbers = data.get("numbers")
    climate = data.get("climate")

    if not userId or not numbers:
        return jsonify({"error": "Missing fields (userId or numbers)"}), 400

    interactions = load_cache()

    # Case 1: Climate provided → store (overwrite if exists) + stream
    # Case 1: Climate provided → store + stream
    if climate:
    # ✅ Only store if exactly 4 numbers
        if len(numbers) == 4:
        # Remove old entry with same userId + numbers
            interactions = [h for h in interactions if not (h["userId"] == userId and h["numbers"] == numbers)]
        # Add latest one
            interactions.append({"userId": userId, "numbers": numbers, "climate": climate})
            save_cache(interactions)

        video_path = os.path.join(VIDEO_DIR, f"{climate}.mp4")
        if not os.path.exists(video_path):
            return jsonify({"error": f"Video for {climate} not found"}), 404

        return send_file(video_path, mimetype="video/mp4")


    # Case 2: Predict climate
    history = [h for h in interactions if h["userId"] == userId]
    if not history:
        return jsonify({"prediction": "Unknown", "reason": "No history yet"})

    best_match, best_score = None, -1
    for h in history:
        score = 0
        for i in range(min(len(h["numbers"]), len(numbers))):
            if h["numbers"][i] == numbers[i]:
                score += 1
            else:
                break
        # Prefer stronger match; if tie, latest entry wins
        if score > best_score or (score == best_score and h == history[-1]):
            best_score, best_match = score, h

    if best_match:
        return jsonify({
            "prediction": best_match["climate"],
            "basedOn": best_match["numbers"],
            "matchScore": best_score
        })
    else:
        return jsonify({"prediction": "Unknown", "reason": "No close match"})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
