from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import numpy as np
import json
import os
from datetime import datetime
import threading
import time
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cloud_gaming_ai_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

class SimpleGameState:
    def __init__(self, player_id):
        self.player_id = player_id
        self.grid = np.zeros((8, 8), dtype=int)
        self.player_position = [0, 0]  # Start at top-left
        self.score = 0
        self.moves_made = 0
        self.move_history = []
        self.game_complete = False
        
        # Initialize the grid with random values
        self._initialize_grid()
        
        # Set player starting position
        self.grid[self.player_position[0], self.player_position[1]] = 0
    
    def _initialize_grid(self):
        """Initialize the 8x8 grid with random values"""
        # Fill grid with random values (1-9)
        self.grid = np.random.randint(1, 10, size=(8, 8))
        
        # Add some special cells
        # Power-ups (values 10-15)
        power_up_positions = random.sample([(i, j) for i in range(8) for j in range(8)], 8)
        for pos in power_up_positions:
            self.grid[pos[0], pos[1]] = random.randint(10, 15)
        
        # Obstacles (value -1)
        obstacle_positions = random.sample([(i, j) for i in range(8) for j in range(8)], 6)
        for pos in obstacle_positions:
            self.grid[pos[0], pos[1]] = -1
        
        # Goal position (value 100)
        goal_positions = [(7, 7)]  # Bottom-right corner
        for pos in goal_positions:
            self.grid[pos[0], pos[1]] = 100
    
    def make_move(self, direction):
        """Make a move in the specified direction"""
        if self.game_complete:
            return False, self.player_position
        
        # Calculate new position
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
        
        # Check if move is valid
        if not self._is_valid_move(new_position):
            return False, self.player_position
        
        # Update player position
        old_position = self.player_position.copy()
        self.player_position = new_position
        
        # Process the cell the player moved to
        cell_value = self.grid[new_position[0], new_position[1]]
        self._process_cell(cell_value, new_position)
        
        # Update grid (mark player position as visited)
        self.grid[new_position[0], new_position[1]] = 0
        
        # Record move
        self.moves_made += 1
        self.move_history.append(direction)
        
        # Check if game is complete
        if cell_value == 100:  # Goal reached
            self.game_complete = True
            self.score += 1000  # Bonus for reaching goal
        
        return True, new_position
    
    def _is_valid_move(self, position):
        """Check if a move to the given position is valid"""
        x, y = position
        
        # Check bounds
        if not (0 <= x < 8 and 0 <= y < 8):
            return False
        
        # Check if position is already visited (value 0)
        if self.grid[x, y] == 0:
            return False
        
        return True
    
    def _process_cell(self, cell_value, position):
        """Process the cell value when player moves to it"""
        if cell_value == -1:  # Obstacle
            self.score -= 10
        elif cell_value == 100:  # Goal
            self.score += 1000
        elif cell_value >= 10:  # Power-up
            self.score += cell_value * 2
        else:  # Regular cell
            self.score += cell_value
    
    def get_move_history(self):
        """Get the move history as a list"""
        return list(self.move_history)
    
    def is_game_complete(self):
        """Check if the game is complete"""
        return self.game_complete

class SimplePredictor:
    def __init__(self):
        self.confidence_scores = []
    
    def predict_next_moves(self, game_state):
        """Simple prediction based on game state analysis"""
        predictions = []
        player_pos = game_state.player_position
        grid = game_state.grid
        
        # Simple heuristic-based predictions
        moves = ['up', 'down', 'left', 'right']
        probabilities = [0.25, 0.25, 0.25, 0.25]  # Equal probability initially
        
        # Adjust probabilities based on game state
        if player_pos[0] > 3:  # Player is in lower half
            probabilities[0] += 0.1  # More likely to go up
            probabilities[1] -= 0.05
        else:  # Player is in upper half
            probabilities[1] += 0.1  # More likely to go down
            probabilities[0] -= 0.05
        
        if player_pos[1] > 3:  # Player is in right half
            probabilities[2] += 0.1  # More likely to go left
            probabilities[3] -= 0.05
        else:  # Player is in left half
            probabilities[3] += 0.1  # More likely to go right
            probabilities[2] -= 0.05
        
        # Normalize probabilities
        total = sum(probabilities)
        probabilities = [p/total for p in probabilities]
        
        # Create predictions
        for i, move in enumerate(moves):
            predictions.append({
                'direction': move,
                'probability': probabilities[i],
                'confidence': min(probabilities[i] * 2, 1.0)
            })
        
        # Sort by probability
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        # Update confidence scores
        if predictions:
            self.confidence_scores.append(predictions[0]['confidence'])
            if len(self.confidence_scores) > 100:
                self.confidence_scores.pop(0)
        
        return predictions
    
    def get_confidence_score(self):
        """Get overall confidence score"""
        if not self.confidence_scores:
            return 0.5
        return sum(self.confidence_scores) / len(self.confidence_scores)

class SimplePrecacheManager:
    def __init__(self):
        self.cache_stats = {}
        self.precached_states = {}
    
    def precache_states(self, predictions, player_id):
        """Simple precaching simulation"""
        if player_id not in self.precached_states:
            self.precached_states[player_id] = 0
        self.precached_states[player_id] += len(predictions)
    
    def calculate_hit_rate(self, player_id):
        """Calculate simple hit rate"""
        return random.uniform(0.3, 0.8)  # Simulated hit rate
    
    def get_overall_hit_rate(self):
        """Get overall hit rate"""
        return random.uniform(0.4, 0.7)
    
    def get_precached_count(self, player_id):
        """Get number of precached states"""
        return self.precached_states.get(player_id, 0)

# Initialize components
ml_predictor = SimplePredictor()
precache_manager = SimplePrecacheManager()
game_states = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Start a new game session with AI prediction"""
    data = request.get_json()
    player_id = data.get('player_id', f'player_{int(time.time())}')
    
    # Initialize game state
    game_state = SimpleGameState(player_id)
    game_states[player_id] = game_state
    
    # Generate initial AI predictions
    predictions = ml_predictor.predict_next_moves(game_state)
    
    # Precache predicted game states
    precache_manager.precache_states(predictions, player_id)
    
    return jsonify({
        'game_id': player_id,
        'grid': game_state.grid.tolist(),
        'player_position': game_state.player_position,
        'ai_predictions': predictions[:5],  # Top 5 predictions
        'score': game_state.score,
        'moves_made': game_state.moves_made
    })

@app.route('/api/game/move', methods=['POST'])
def make_move():
    """Process player move and return AI predictions"""
    data = request.get_json()
    player_id = data.get('player_id')
    direction = data.get('direction')  # 'up', 'down', 'left', 'right'
    
    if player_id not in game_states:
        return jsonify({'error': 'Game not found'}), 404
    
    game_state = game_states[player_id]
    
    # Make the move
    success, new_position = game_state.make_move(direction)
    
    if not success:
        return jsonify({'error': 'Invalid move'}), 400
    
    # Generate new predictions for next moves
    predictions = ml_predictor.predict_next_moves(game_state)
    
    # Precache new predicted states
    precache_manager.precache_states(predictions, player_id)
    
    # Check if any predicted states match current state (hit rate)
    hit_rate = precache_manager.calculate_hit_rate(player_id)
    
    return jsonify({
        'success': True,
        'new_position': new_position,
        'grid': game_state.grid.tolist(),
        'score': game_state.score,
        'ai_predictions': predictions[:5],
        'prediction_accuracy': hit_rate,
        'moves_made': game_state.moves_made,
        'game_completed': game_state.is_game_complete()
    })

@app.route('/api/game/stats', methods=['GET'])
def get_game_stats():
    """Get AI prediction statistics"""
    player_id = request.args.get('player_id')
    
    if player_id and player_id in game_states:
        game_state = game_states[player_id]
        hit_rate = precache_manager.calculate_hit_rate(player_id)
        
        return jsonify({
            'total_moves': game_state.moves_made,
            'prediction_accuracy': hit_rate,
            'score': game_state.score,
            'ai_confidence': ml_predictor.get_confidence_score(),
            'precached_states': precache_manager.get_precached_count(player_id)
        })
    
    return jsonify({
        'total_games': len(game_states),
        'overall_accuracy': precache_manager.get_overall_hit_rate(),
        'ai_confidence': ml_predictor.get_confidence_score()
    })

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection for real-time updates"""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print('Client disconnected')

@socketio.on('request_prediction')
def handle_prediction_request(data):
    """Handle real-time prediction requests"""
    player_id = data.get('player_id')
    
    if player_id in game_states:
        game_state = game_states[player_id]
        predictions = ml_predictor.predict_next_moves(game_state)
        
        emit('ai_prediction', {
            'predictions': predictions[:3],
            'confidence': ml_predictor.get_confidence_score(),
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    print("🤖 AI Predictive Cloud Gaming Server Starting...")
    print("📊 Using Basic AI Prediction System")
    print("🌐 Server will be available at: http://localhost:5000")
    print("🎮 Open your browser and start playing!")
    print("🎯 Use arrow keys or WASD to move around the grid!")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 