#!/usr/bin/env python3
"""
Jeopardy Game - Player Simulator
Simulates 30 players joining and buzzing in for testing
"""

import sys
import subprocess

# Check for required packages
def check_dependencies():
    """Check and install required packages"""
    required = {
        'socketio': 'python-socketio',
        'websocket': 'websocket-client'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"\n{'='*60}")
        print("Installing required packages...")
        print(f"{'='*60}\n")
        for package in missing:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'])
        print("\n✓ All packages installed!\n")

check_dependencies()

import socketio
import time
import random
import threading
from datetime import datetime

# Configuration
SERVER_URL = 'http://localhost:5000'
NUM_PLAYERS = 30
BUZZ_DELAY_MIN = 0.1  # Minimum seconds before buzzing
BUZZ_DELAY_MAX = 2.0  # Maximum seconds before buzzing

# Player names
PLAYER_NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Eve",
    "Frank", "Grace", "Henry", "Iris", "Jack",
    "Kate", "Liam", "Maya", "Noah", "Olivia",
    "Paul", "Quinn", "Rachel", "Sam", "Tina",
    "Uma", "Victor", "Wendy", "Xander", "Yara",
    "Zack", "Amy", "Ben", "Cara", "Dan", "Ella"
]

class PlayerBot:
    """Simulates a single player"""
    
    def __init__(self, name, player_id):
        self.name = name
        self.player_id = player_id
        self.sio = socketio.Client(reconnection=True)
        self.connected = False
        self.registered = False
        self.can_buzz = False
        self.has_buzzed = False
        
        # Setup event handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup SocketIO event handlers"""
        
        @self.sio.on('connect')
        def on_connect():
            self.connected = True
            print(f"[{self.name}] Connected to server")
            # Register immediately
            time.sleep(0.1)
            self.register()
        
        @self.sio.on('disconnect')
        def on_disconnect():
            self.connected = False
            print(f"[{self.name}] Disconnected from server")
        
        @self.sio.on('join_success')
        def on_join_success(data=None):
            self.registered = True
            print(f"[{self.name}] ✓ Registered successfully")
        
        @self.sio.on('join_failed')
        def on_join_failed(data=None):
            message = data.get('message', 'Unknown error') if data else 'Unknown error'
            print(f"[{self.name}] ✗ Registration failed: {message}")
        
        @self.sio.on('buzzing_opened')
        def on_buzzing_opened(data=None):
            self.can_buzz = True
            self.has_buzzed = False
            print(f"[{self.name}] Buzzing opened!")
            # Buzz after random delay
            delay = random.uniform(BUZZ_DELAY_MIN, BUZZ_DELAY_MAX)
            threading.Timer(delay, self.buzz).start()
        
        @self.sio.on('buzz_confirmed')
        def on_buzz_confirmed(data=None):
            position = data.get('position', '?') if data else '?'
            print(f"[{self.name}] 🔔 BUZZED IN at position #{position}")
        
        @self.sio.on('final_jeopardy_question_revealed')
        def on_fj_question_revealed(data=None):
            print(f"[{self.name}] Final Jeopardy question received!")
            # Submit answer after random delay (5-20 seconds)
            delay = random.uniform(5, 20)
            threading.Timer(delay, self.submit_fj_answer).start()
        
        @self.sio.on('answer_judged')
        def on_answer_judged(data=None):
            if not data:
                return
            if data.get('player') == self.name:
                if data.get('correct'):
                    value = data.get('value', 0)
                    print(f"[{self.name}] ✓ CORRECT! +${value}")
                else:
                    print(f"[{self.name}] ✗ INCORRECT")
    
    def connect(self):
        """Connect to server"""
        try:
            self.sio.connect(SERVER_URL)
            return True
        except Exception as e:
            print(f"[{self.name}] Failed to connect: {e}")
            return False
    
    def register(self):
        """Register player"""
        if not self.connected:
            print(f"[{self.name}] Cannot register - not connected")
            return
        
        try:
            self.sio.emit('player_join', {'name': self.name})
        except Exception as e:
            print(f"[{self.name}] Failed to register: {e}")
    
    def buzz(self):
        """Buzz in"""
        if not self.can_buzz or self.has_buzzed:
            return
        
        try:
            self.sio.emit('player_buzz', {'name': self.name})
            self.has_buzzed = True
        except Exception as e:
            print(f"[{self.name}] Failed to buzz: {e}")
    
    def submit_fj_answer(self):
        """Submit Final Jeopardy answer"""
        if not self.connected:
            return
        
        try:
            # Generate random gibberish answer
            answers = [
                "Who is Napoleon Bonaparte?",
                "What is the Theory of Relativity?",
                "Who is Shakespeare?",
                "What is photosynthesis?",
                "Who is Abraham Lincoln?",
                "What is the Pythagorean Theorem?",
                "Who is Cleopatra?",
                "What is DNA?",
                "Who is Beethoven?",
                "What is the Big Bang?",
                "Uhhh... Bob?",
                "I have no idea",
                "What is... something?",
                "42",
                "The answer is definitely maybe",
                "Who is that guy?",
                "What is that thing?",
                "I'll take a wild guess: George Washington",
                "Is it cheese?",
                "What is love? Baby don't hurt me"
            ]
            
            answer = random.choice(answers)
            self.sio.emit('player_submit_fj', {
                'name': self.name,
                'answer': answer
            })
            print(f"[{self.name}] 📝 Submitted FJ answer: \"{answer}\"")
        except Exception as e:
            print(f"[{self.name}] Failed to submit FJ answer: {e}")
    
    def disconnect(self):
        """Disconnect from server"""
        try:
            self.sio.disconnect()
        except:
            pass


class GameSimulator:
    """Manages all player bots"""
    
    def __init__(self, num_players=30):
        self.num_players = num_players
        self.bots = []
        self.running = False
    
    def create_bots(self):
        """Create player bots"""
        print(f"\n{'='*60}")
        print(f"Creating {self.num_players} player bots...")
        print(f"{'='*60}\n")
        
        for i in range(self.num_players):
            name = PLAYER_NAMES[i] if i < len(PLAYER_NAMES) else f"Player{i+1}"
            bot = PlayerBot(name, i+1)
            self.bots.append(bot)
    
    def connect_all(self):
        """Connect all bots to server"""
        print(f"\n{'='*60}")
        print(f"Connecting {self.num_players} players to server...")
        print(f"{'='*60}\n")
        
        for i, bot in enumerate(self.bots):
            # Stagger connections slightly
            time.sleep(0.1)
            threading.Thread(target=bot.connect, daemon=True).start()
            
            # Progress update every 5 players
            if (i + 1) % 5 == 0:
                print(f"[SIMULATOR] Connected {i+1}/{self.num_players} players...")
        
        # Wait for all to connect
        time.sleep(2)
        
        # Count successful connections
        connected = sum(1 for bot in self.bots if bot.connected)
        registered = sum(1 for bot in self.bots if bot.registered)
        
        print(f"\n{'='*60}")
        print(f"Connection Results:")
        print(f"  Connected: {connected}/{self.num_players}")
        print(f"  Registered: {registered}/{self.num_players}")
        print(f"{'='*60}\n")
    
    def disconnect_all(self):
        """Disconnect all bots"""
        print(f"\n{'='*60}")
        print(f"Disconnecting all players...")
        print(f"{'='*60}\n")
        
        for bot in self.bots:
            bot.disconnect()
        
        time.sleep(1)
        print("[SIMULATOR] All players disconnected")
    
    def status_monitor(self):
        """Monitor and display status"""
        while self.running:
            time.sleep(5)
            connected = sum(1 for bot in self.bots if bot.connected)
            registered = sum(1 for bot in self.bots if bot.registered)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Status - Connected: {connected}, Registered: {registered}")
    
    def run(self):
        """Run the simulation"""
        self.running = True
        
        print("\n" + "="*60)
        print("JEOPARDY GAME - PLAYER SIMULATOR")
        print("="*60)
        print(f"Server: {SERVER_URL}")
        print(f"Players: {self.num_players}")
        print(f"Buzz delay: {BUZZ_DELAY_MIN}-{BUZZ_DELAY_MAX}s")
        print("="*60 + "\n")
        
        # Create bots
        self.create_bots()
        
        # Start status monitor
        monitor_thread = threading.Thread(target=self.status_monitor, daemon=True)
        monitor_thread.start()
        
        # Connect all bots
        self.connect_all()
        
        print("\n" + "="*60)
        print("SIMULATION RUNNING")
        print("="*60)
        print("Players are connected and ready to buzz!")
        print("On the host panel:")
        print("  1. Start the game")
        print("  2. Select a question")
        print("  3. Open buzzing")
        print("  4. Watch all 30 players buzz in!")
        print("\nPress Ctrl+C to stop simulation")
        print("="*60 + "\n")
        
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping simulation...")
            self.running = False
            self.disconnect_all()


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("JEOPARDY GAME - PLAYER SIMULATOR")
    print("="*60)
    print()
    
    # Get number of players
    try:
        num = input(f"Number of players to simulate (default {NUM_PLAYERS}): ").strip()
        num_players = int(num) if num else NUM_PLAYERS
    except ValueError:
        num_players = NUM_PLAYERS
    
    # Confirm
    print(f"\nSimulating {num_players} players...")
    print(f"Make sure the Jeopardy server is running at {SERVER_URL}")
    
    input("\nPress Enter to start simulation...")
    
    # Create and run simulator
    simulator = GameSimulator(num_players)
    simulator.run()


if __name__ == '__main__':
    main()
