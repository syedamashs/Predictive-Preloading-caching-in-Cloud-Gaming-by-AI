#!/usr/bin/env python3
"""
Simple test script to verify the game functionality
"""

import requests
import json
import time

def test_game():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing AI Predictive Cloud Gaming...")
    
    # Test 1: Start a new game
    print("\n1. Starting new game...")
    try:
        response = requests.post(f"{base_url}/api/game/start", 
                               json={"player_id": "test_player"})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Game started successfully!")
            print(f"   Game ID: {data['game_id']}")
            print(f"   Player Position: {data['player_position']}")
            print(f"   Score: {data['score']}")
            print(f"   AI Predictions: {len(data['ai_predictions'])} predictions generated")
            
            game_id = data['game_id']
            player_pos = data['player_position']
            
            # Test 2: Make a move
            print("\n2. Testing move functionality...")
            move_response = requests.post(f"{base_url}/api/game/move", 
                                        json={"player_id": game_id, "direction": "right"})
            
            if move_response.status_code == 200:
                move_data = move_response.json()
                print(f"✅ Move successful!")
                print(f"   New Position: {move_data['new_position']}")
                print(f"   New Score: {move_data['score']}")
                print(f"   Moves Made: {move_data['moves_made']}")
                print(f"   AI Predictions Updated: {len(move_data['ai_predictions'])} predictions")
                
                # Test 3: Get game stats
                print("\n3. Testing AI statistics...")
                stats_response = requests.get(f"{base_url}/api/game/stats?player_id={game_id}")
                
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    print(f"✅ Stats retrieved successfully!")
                    print(f"   Total Moves: {stats_data['total_moves']}")
                    print(f"   Prediction Accuracy: {stats_data['prediction_accuracy']:.2%}")
                    print(f"   AI Confidence: {stats_data['ai_confidence']:.2%}")
                    print(f"   Precached States: {stats_data['precached_states']}")
                
                else:
                    print(f"❌ Failed to get stats: {stats_response.status_code}")
            else:
                print(f"❌ Move failed: {move_response.status_code}")
                print(f"   Error: {move_response.text}")
        else:
            print(f"❌ Failed to start game: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on http://localhost:5000")
        print("   Run: python game_working.py")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_game() 