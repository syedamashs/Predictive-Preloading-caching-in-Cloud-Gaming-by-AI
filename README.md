# 🌦️ Predictive Climate Game

An interactive web-based game demonstrating **AI-powered predictive preloading and streaming for climate scenarios**. The game predicts likely climate videos based on user number inputs and preloads them for seamless viewing, showcasing AI-assisted prefetching in a cloud-like environment.

---

## 🎮 Game Features

- **4-Number Input System**: Enter a 4-digit combination to trigger predictions.
- **AI Prediction Engine**: Real-time prediction of climate conditions based on number inputs.
- **Video Preloading & Streaming**: Seamless preloading of predicted videos to reduce wait times.
- **Manual Override**: Select and play actual climate videos from a dropdown menu.
- **Responsive UI**: Clean, modern, and mobile-friendly design.

---

## 🧠 AI Components

### Prediction Engine:

- **Pattern Recognition**: Analyze input numbers to predict climate.
- **Match Scoring**: Measure prediction confidence using historical data.
- **Preloading System**: Prefetch predicted climate videos to reduce latency.
- **Fallback Handling**: Displays "No prediction yet" if confidence is low.

---

## 🚀 Streaming & Preloading Features

### Predictive Preloading:

- Automatically fetches the predicted climate video in the background.
- Reduces waiting time when the prediction is displayed.
- Displays loading and success/failure status for preloaded videos.

### Manual Play:

- Users can manually choose a climate video from the dropdown menu.
- Stream the chosen video instantly.

---

## 📋 Game Rules

1. **Objective**: Enter numbers to trigger AI prediction.
2. **Prediction**: The AI evaluates your input and predicts one of three climates: Sunny, Rainy, or Snowy.
3. **Video Playback**:
   - Preloaded videos play instantly.
   - Manual selection overrides preloading.
4. **Clear Input**: The "Clear" button resets all inputs, hides prediction, and removes preloaded videos.

---

## 🛠️ Installation & Setup

### Prerequisites:

- Python 3.8 or higher
- Flask (or any compatible backend)
- Modern web browser

### Steps:

1. **Clone the repository** or download project files.
2. **Install dependencies** (for Flask backend):
   ```bash
   pip install -r requirements.txt
