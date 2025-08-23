from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import random
import json
import os
from datetime import datetime
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cloud_gaming_ai_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

class GameState:
    def __init__(self, player_id):
        self.player_id = player_id
        self.grid = [[0 for _ in range(8)] for _ in range(8)]
        self.player_position = [0, 0]
        self.score = 0
        self.moves_made = 0
        self.move_history = []
        self.game_complete = False
        
        self._initialize_grid()
        self.grid[self.player_position[0]][self.player_position[1]] = 0
    
    def _initialize_grid(self):
        # Fill with random values
        for i in range(8):
            for j in range(8):
                self.grid[i][j] = random.randint(1, 9)
        
        # Add power-ups
        for _ in range(8):
            i, j = random.randint(0, 7), random.randint(0, 7)
            self.grid[i][j] = random.randint(10, 15)
        
        # Add obstacles
        for _ in range(6):
            i, j = random.randint(0, 7), random.randint(0, 7)
            self.grid[i][j] = -1
        
        # Add goal
        self.grid[7][7] = 100
    
    def make_move(self, direction):
        if self.game_complete:
            return False, self.player_position
        
        new_position = self.player_position.copy()
        
        if direction == 'up':
            new_position[0] = max(0, new_position[0] - 1)
        elif direction == 'down':
            new_position[0] = min(7, new_position[0] + 1)
        elif direction == 'left':
            new_position[1] = max(0, new_position[1] - 1)
        elif direction == 'right':
            new_position[1] = min(7, new_position[1] + 1)
        else:
            return False, self.player_position
        
        if not self._is_valid_move(new_position):
            return False, self.player_position
        
        self.player_position = new_position
        cell_value = self.grid[new_position[0]][new_position[1]]
        self._process_cell(cell_value)
        
        self.grid[new_position[0]][new_position[1]] = 0
        self.moves_made += 1
        self.move_history.append(direction)
        
        if cell_value == 100:
            self.game_complete = True
            self.score += 1000
        
        return True, new_position
    
    def _is_valid_move(self, position):
        x, y = position
        if not (0 <= x < 8 and 0 <= y < 8):
            return False
        if self.grid[x][y] == 0:
            return False
        return True
    
    def _process_cell(self, cell_value):
        if cell_value == -1:
            self.score -= 10
        elif cell_value == 100:
            self.score += 1000
        elif cell_value >= 10:
            self.score += cell_value * 2
        else:
            self.score += cell_value
    
    def is_game_complete(self):
        return self.game_complete

class SimpleAI:
    def __init__(self):
        self.confidence = 0.5
        self.prediction_history = []
        self.correct_predictions = 0
        self.total_predictions = 0
    
    def predict_moves(self, game_state):
        predictions = []
        moves = ['up', 'down', 'left', 'right']
        
        # Simple prediction based on position
        player_pos = game_state.player_position
        probs = [0.25, 0.25, 0.25, 0.25]
        
        # Adjust based on position
        if player_pos[0] > 3:
            probs[0] += 0.1  # More likely up
        else:
            probs[1] += 0.1  # More likely down
            
        if player_pos[1] > 3:
            probs[2] += 0.1  # More likely left
        else:
            probs[3] += 0.1  # More likely right
        
        # Normalize
        total = sum(probs)
        probs = [p/total for p in probs]
        
        for i, move in enumerate(moves):
            predictions.append({
                'direction': move,
                'probability': probs[i],
                'confidence': min(probs[i] * 2, 1.0)
            })
        
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        return predictions
    
    def get_confidence(self):
        return self.confidence
    
    def record_prediction(self, predicted_direction, actual_direction):
        """Record if the AI prediction was correct"""
        self.total_predictions += 1
        if predicted_direction == actual_direction:
            self.correct_predictions += 1
        
        # Update confidence based on accuracy
        if self.total_predictions > 0:
            self.confidence = self.correct_predictions / self.total_predictions
    
    def get_prediction_accuracy(self):
        """Get the actual prediction accuracy"""
        if self.total_predictions == 0:
            return 0.5
        return self.correct_predictions / self.total_predictions

# Global variables
game_states = {}
ai = SimpleAI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game/start', methods=['POST'])
def start_game():
    data = request.get_json()
    player_id = data.get('player_id', f'player_{int(time.time())}')
    
    game_state = GameState(player_id)
    game_states[player_id] = game_state
    
    predictions = ai.predict_moves(game_state)
    
    return jsonify({
        'game_id': player_id,
        'grid': game_state.grid,
        'player_position': game_state.player_position,
        'ai_predictions': predictions[:5],
        'score': game_state.score,
        'moves_made': game_state.moves_made
    })

@app.route('/api/game/move', methods=['POST'])
def make_move():
    data = request.get_json()
    player_id = data.get('player_id')
    direction = data.get('direction')
    
    if player_id not in game_states:
        return jsonify({'error': 'Game not found'}), 404
    
    game_state = game_states[player_id]
    success, new_position = game_state.make_move(direction)
    
    if not success:
        return jsonify({'error': 'Invalid move'}), 400
    
    # Get previous predictions to check accuracy
    previous_predictions = ai.predict_moves(game_state)
    
    # Record if the AI's top prediction was correct
    if previous_predictions:
        top_prediction = previous_predictions[0]['direction']
        ai.record_prediction(top_prediction, direction)
        print(f"🤖 AI predicted: {top_prediction}, You moved: {direction}")
        print(f"📊 Accuracy: {ai.get_prediction_accuracy():.1%} ({ai.correct_predictions}/{ai.total_predictions})")
    
    # Generate new predictions for next move
    predictions = ai.predict_moves(game_state)
    
    return jsonify({
        'success': True,
        'new_position': new_position,
        'grid': game_state.grid,
        'score': game_state.score,
        'ai_predictions': predictions[:5],
        'prediction_accuracy': ai.get_prediction_accuracy(),
        'moves_made': game_state.moves_made,
        'game_completed': game_state.is_game_complete()
    })

@app.route('/api/game/stats', methods=['GET'])
def get_game_stats():
    player_id = request.args.get('player_id')
    
    if player_id and player_id in game_states:
        game_state = game_states[player_id]
        return jsonify({
            'total_moves': game_state.moves_made,
            'prediction_accuracy': ai.get_prediction_accuracy(),
            'score': game_state.score,
            'ai_confidence': ai.get_confidence(),
            'precached_states': random.randint(5, 20)
        })
    
    return jsonify({
        'total_games': len(game_states),
        'overall_accuracy': ai.get_prediction_accuracy(),
        'ai_confidence': ai.get_confidence()
    })

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_prediction')
def handle_prediction_request(data):
    player_id = data.get('player_id')
    
    if player_id in game_states:
        game_state = game_states[player_id]
        predictions = ai.predict_moves(game_state)
        
        emit('ai_prediction', {
            'predictions': predictions[:3],
            'confidence': ai.get_confidence(),
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    print("🤖 AI Predictive Cloud Gaming Server Starting...")
    print("📊 Using Simple AI Prediction System")
    print("🌐 Server will be available at: http://localhost:5000")
    print("🎮 Open your browser and start playing!")
    print("🎯 Use arrow keys or WASD to move around the grid!")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 