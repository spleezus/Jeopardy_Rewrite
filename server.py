"""
Jeopardy Game Server - Production Ready for 20-30 Players
Server-authoritative architecture with race condition protection

Python 3.8-3.12 compatible (uses gevent for async support)
"""

import os
import csv
import threading
import time
import socket
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jeopardy-secret-key-change-in-production'
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# ============================================================================
# GLOBAL STATE (Server Authoritative)
# ============================================================================

class GameState:
    """Thread-safe game state container"""
    def __init__(self):
        self.lock = threading.RLock()  # Reentrant lock for nested calls
        
        # Game metadata
        self.game_name = ""
        self.host_password = ""
        self.categories = []  # List of 5 category names
        self.board = []  # 5x5 grid: [{question, answer, value, used}, ...]
        self.fj_question = ""
        self.fj_answer = ""
        self.fj_enabled = True
        self.fj_value = 0
        
        # Active game state
        self.game_started = False
        self.current_question = None  # {row, col, question, answer, value}
        self.question_revealed = False  # Track if question is shown to players
        self.buzzing_open = False
        self.buzzer_queue = []  # [{player_name, timestamp}, ...]
        self.current_selector = None  # Player name who picks next
        self.answer_judged = False  # Track if answer has been judged
        self.player_results = {}  # Track correct/incorrect per player per question
        self.show_answer = False  # NEW: Track if answer should be shown
        
        # Players: {name: {score, socket_id, connected, last_seen}}
        self.players = {}
        
        # Final Jeopardy
        self.fj_active = False
        self.fj_question_revealed = False  # Track if FJ question shown to players/TV
        self.fj_submissions = {}  # {player_name: {answer, wager}}
        
        # Host
        self.host_connected = False
        self.host_socket_id = None
        
        # Debug mode
        self.debug_mode = False

game = GameState()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_local_ip():
    """Get the local IP address of the server"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def load_csv(filepath):
    """Load and parse the game CSV file - UPDATED for new format with encoding fallback"""
    with game.lock:
        try:
            # Try UTF-8 first
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
            except UnicodeDecodeError:
                # Fallback to Windows-1252 (handles smart quotes)
                with open(filepath, 'r', encoding='windows-1252') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
            
            if len(rows) < 13:
                return False, "CSV must have at least 13 rows"
            
            # Parse metadata
            # Row 0: Game Title:, Jeopardy Test Game
            game.game_name = rows[0][1] if len(rows[0]) > 1 else "Jeopardy Game"
            
            # Row 1: Host Password, host123
            game.host_password = rows[1][1] if len(rows[1]) > 1 else "host123"
            
            # Row 2: Empty
            # Row 3: Basic Jeopardy
            # Row 4: Categories
            game.categories = [rows[4][i] if i < len(rows[4]) and rows[4][i] else f"Category {i+1}" 
                             for i in range(5)]
            
            # Parse 5x5 board (rows 5-9) - questions with | separator
            game.board = []
            values = [1, 2, 3, 4, 5]
            
            for row_idx in range(5):
                csv_row = rows[5 + row_idx] if (5 + row_idx) < len(rows) else []
                for col_idx in range(5):
                    cell = csv_row[col_idx] if col_idx < len(csv_row) else "Question|Answer"
                    
                    # Split on FIRST | only to handle pipes in questions
                    if '|' in cell:
                        parts = cell.split('|', 1)  # Split on first | only
                        question = parts[0].strip()
                        answer = parts[1].strip() if len(parts) > 1 else "Answer"
                    else:
                        question = cell.strip() if cell.strip() else "Question"
                        answer = "Answer"
                    
                    game.board.append({
                        'row': row_idx,
                        'col': col_idx,
                        'question': question,
                        'answer': answer,
                        'value': values[row_idx],
                        'used': False
                    })
            
            # Parse Final Jeopardy (row 12)
            # Row 10: Empty
            # Row 11: Final Jeopardy
            # Row 12: Question|Answer, Value
            if len(rows) > 12 and len(rows[12]) > 0:
                fj_cell = rows[12][0]
                if '|' in fj_cell:
                    fj_parts = fj_cell.split('|', 1)
                    game.fj_question = fj_parts[0].strip()
                    game.fj_answer = fj_parts[1].strip() if len(fj_parts) > 1 else "Final Answer"
                else:
                    game.fj_question = fj_cell.strip()
                    game.fj_answer = "Final Answer"
                
                # Read FJ value from column 1 (optional)
                if len(rows[12]) > 1 and rows[12][1].strip().isdigit():
                    game.fj_value = int(rows[12][1].strip())
                else:
                    game.fj_value = 5  # Default to $5
            
            print(f"\nLoaded {game.game_name}")
            print(f"Categories: {game.categories}")
            print(f"Questions: {len(game.board)}")
            print(f"FJ Question: {game.fj_question[:50]}...")
            
            return True, "CSV loaded successfully"
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error loading CSV: {str(e)}"

def broadcast_game_state():
    """Broadcast current game state to all clients"""
    with game.lock:
        state = {
            'game_name': game.game_name,
            'categories': game.categories,
            'board': game.board,
            'current_question': game.current_question,
            'question_revealed': game.question_revealed,
            'buzzing_open': game.buzzing_open,
            'buzzer_queue': game.buzzer_queue,
            'current_selector': game.current_selector,
            'game_started': game.game_started,
            'fj_active': game.fj_active,
            'fj_value': game.fj_value,
            'answer_judged': game.answer_judged,
            'player_results': game.player_results,
            'show_answer': game.show_answer,
            'players': {name: {'score': p['score'], 'connected': p['connected']} 
                       for name, p in game.players.items()}
        }
    
    socketio.emit('game_state', state)

def broadcast_scores():
    """Broadcast just the scores (lighter weight)"""
    with game.lock:
        scores = {name: p['score'] for name, p in game.players.items()}
    
    socketio.emit('scores_update', scores)

def check_all_questions_used():
    """Check if all questions have been used"""
    with game.lock:
        all_used = all(q['used'] for q in game.board)
        if all_used and game.fj_enabled and not game.fj_active:
            # Notify that all questions are complete
            socketio.emit('all_questions_complete', {}, room='host')
            return True
    return False

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def tv_display():
    """TV Display screen"""
    return render_template('tv.html', server_ip=get_local_ip(), port=5000)

@app.route('/host')
def host_control():
    """Host control panel"""
    return render_template('host.html')

@app.route('/player')
def player_interface():
    """Player interface"""
    return render_template('player.html')

@app.route('/api/server-info')
def server_info():
    """Return server IP for QR code generation"""
    return jsonify({
        'ip': get_local_ip(),
        'port': 5000
    })

# ============================================================================
# SOCKETIO EVENTS - HOST
# ============================================================================

@socketio.on('host_authenticate')
def handle_host_auth(data):
    """Authenticate host"""
    with game.lock:
        if game.host_connected and game.host_socket_id != request.sid:
            emit('auth_failed', {'message': 'Host already connected'})
            return
        
        if data.get('password') == game.host_password:
            game.host_connected = True
            game.host_socket_id = request.sid
            join_room('host')
            emit('auth_success', {'message': 'Host authenticated'})
            emit('game_state', {
                'game_name': game.game_name,
                'categories': game.categories,
                'board': game.board,
                'players': {name: {'score': p['score'], 'connected': p['connected']} 
                           for name, p in game.players.items()},
                'fj_enabled': game.fj_enabled,
                'fj_value': game.fj_value,
                'debug_mode': game.debug_mode
            })
        else:
            emit('auth_failed', {'message': 'Invalid password'})

@socketio.on('host_start_game')
def handle_start_game():
    """Start the game and begin category reveal animation"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        game.game_started = True
        game.current_selector = None
    
    # Start category reveal animation
    socketio.emit('begin_category_reveal', {
        'categories': game.categories
    })
    
    # Wait 2 seconds then reveal categories one by one
    # Client will handle the animation
    broadcast_game_state()

@socketio.on('host_select_question')
def handle_select_question(data):
    """Host selects a question (after player verbally tells them)"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        # Check if previous question was judged
        if game.current_question and not game.answer_judged:
            emit('error', {'message': 'Please judge current question first or assign next selector'})
            return
        
        row = data.get('row')
        col = data.get('col')
        
        # Find the question
        question_data = None
        for q in game.board:
            if q['row'] == row and q['col'] == col and not q['used']:
                question_data = q
                break
        
        if not question_data:
            emit('error', {'message': 'Question not available'})
            return
        
        # Mark as used
        question_data['used'] = True
        
        # Set as current question (but NOT revealed yet)
        game.current_question = {
            'row': row,
            'col': col,
            'question': question_data['question'],
            'answer': question_data['answer'],
            'value': question_data['value']
        }
        
        # Reset state for new question
        game.question_revealed = False
        game.buzzing_open = False
        game.buzzer_queue = []
        game.answer_judged = False
        game.player_results = {}
        game.show_answer = False
    
    broadcast_game_state()

@socketio.on('host_reveal_question')
def handle_reveal_question():
    """Host reveals the question to players"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        if not game.current_question:
            return
        
        game.question_revealed = True
    
    broadcast_game_state()

@socketio.on('host_open_buzzing')
def handle_open_buzzing():
    """Host opens buzzing - also reveals question to players"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        game.buzzing_open = True
        game.buzzer_queue = []
        game.question_revealed = True  # Auto-reveal when buzzing opens
    
    socketio.emit('buzzing_opened', {})
    broadcast_game_state()

@socketio.on('host_close_buzzing')
def handle_close_buzzing():
    """Host closes buzzing"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        game.buzzing_open = False
    
    broadcast_game_state()

@socketio.on('host_judge_answer')
def handle_judge_answer(data):
    """Host judges an answer as correct or incorrect"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        player_name = data.get('player')
        is_correct = data.get('correct', False)
        
        if player_name not in game.players:
            return
        
        value = game.current_question.get('value', 0) if game.current_question else 0
        
        # Track result for display
        game.player_results[player_name] = is_correct
        
        if is_correct:
            # Check if points already awarded for this question
            points_awarded = False
            if not game.answer_judged:
                # Award points only once
                game.players[player_name]['score'] += value
                points_awarded = True
            
            # Set as next selector (even if not first correct, last correct becomes selector)
            game.current_selector = player_name
            
            # Mark question as judged (prevents multiple point awards)
            game.answer_judged = True
            
            # Show answer on TV
            game.show_answer = True
            
            # Close buzzing but KEEP queue visible with results
            game.buzzing_open = False
            # DON'T clear queue - keep it visible with check/X marks
            # game.buzzer_queue = []
            
            # Emit judgment - only show value if points were actually awarded
            socketio.emit('answer_judged', {
                'player': player_name,
                'correct': True,
                'value': value if points_awarded else 0,  # Only show value if first correct
                'answer': game.current_question.get('answer', ''),
                'next_selector': player_name
            })
            
        else:
            # No point deduction per requirements
            
            # DO NOT remove from buzzer queue - keep them visible with X mark
            # game.buzzer_queue = [b for b in game.buzzer_queue if b['player'] != player_name]
            
            # Emit judgment
            socketio.emit('answer_judged', {
                'player': player_name,
                'correct': False,
                'value': 0,  # No deduction
                'next_selector': game.current_selector  # Include current selector
            })
    
    broadcast_scores()
    broadcast_game_state()
    
    # Check if all questions used
    check_all_questions_used()

@socketio.on('host_no_winner')
def handle_no_winner(data):
    """Host manually assigns next selector when no one answers correctly"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        next_selector = data.get('next_selector')
        award_points = data.get('award_points', False)
        
        if next_selector and next_selector in game.players:
            game.current_selector = next_selector
            
            # Award points if checkbox checked
            if award_points and game.current_question:
                value = game.current_question.get('value', 0)
                game.players[next_selector]['score'] += value
        
        # Mark question as judged so host can select next question
        game.answer_judged = True
        game.buzzing_open = False
        # DON'T clear queue - keep it visible with check/X marks
        # game.buzzer_queue = []
        game.show_answer = True  # Show answer on no winner too
    
    # Emit no winner event with answer
    socketio.emit('no_winner_assigned', {
        'next_selector': next_selector,
        'answer': game.current_question.get('answer', '') if game.current_question else ''
    })
    
    broadcast_scores()
    broadcast_game_state()
    
    # Check if all questions used
    check_all_questions_used()

@socketio.on('host_jump_to_final_jeopardy')
def handle_jump_to_fj():
    """Jump to Final Jeopardy - mark all questions as used"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        # Mark all questions as used
        for question in game.board:
            question['used'] = True
        
        # Clear current question state
        game.current_question = None
        game.buzzing_open = False
        game.buzzer_queue = []
        game.answer_judged = True
    
    broadcast_game_state()
    
    # Trigger FJ available notification
    socketio.emit('all_questions_complete', room='host')

@socketio.on('host_start_final_jeopardy')
def handle_start_fj():
    """Start Final Jeopardy - don't show question yet"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        if not game.fj_enabled:
            return
        
        game.fj_active = True
        game.fj_question_revealed = False
        game.fj_submissions = {}
        game.current_question = None
        game.buzzing_open = False
    
    # Only notify host, don't show question to players/TV yet
    socketio.emit('final_jeopardy_started_host', {
        'question': game.fj_question,
        'value': game.fj_value
    }, room='host')
    
    broadcast_game_state()

@socketio.on('host_show_fj_question')
def handle_show_fj_question():
    """Show FJ question to players and TV"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        game.fj_question_revealed = True
    
    # Broadcast question to everyone
    socketio.emit('final_jeopardy_question_revealed', {
        'question': game.fj_question,
        'value': game.fj_value
    })
    
    broadcast_game_state()

@socketio.on('host_show_fj_question')
def handle_show_fj_question():
    """Show Final Jeopardy question to players and TV"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        game.fj_question_revealed = True
    
    # Broadcast to players and TV using existing event name
    socketio.emit('final_jeopardy_question_revealed', {
        'question': game.fj_question,
        'value': game.fj_value
    })
    
    broadcast_game_state()

@socketio.on('host_reveal_fj_answers')
def handle_reveal_fj():
    """Reveal Final Jeopardy answers"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        submissions = {name: {
            'answer': sub['answer'], 
            'wager': sub['wager'],
            'correct': sub.get('correct', False)
        } for name, sub in game.fj_submissions.items()}
        correct_answer = game.fj_answer
    
    socketio.emit('fj_answers_revealed', {
        'submissions': submissions,
        'correct_answer': correct_answer
    })

@socketio.on('host_judge_fj_single')
def handle_judge_fj_single(data):
    """Judge a single Final Jeopardy answer"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        player_name = data.get('player')
        is_correct = data.get('correct', False)
        
        if player_name not in game.fj_submissions:
            return
        
        # Mark answer as correct/incorrect
        game.fj_submissions[player_name]['correct'] = is_correct
        
        # Award points if correct AND not already awarded
        if is_correct and player_name in game.players:
            # Check if points already awarded (prevent multiple awards)
            if not game.fj_submissions[player_name].get('points_awarded', False):
                game.players[player_name]['score'] += game.fj_value
                game.fj_submissions[player_name]['points_awarded'] = True
        
        # Track result for display (same as regular questions)
        game.player_results[player_name] = is_correct
    
    # Broadcast to TV to show check/X mark immediately
    socketio.emit('fj_single_judged', {
        'player': player_name,
        'correct': is_correct
    })
    
    broadcast_scores()

@socketio.on('host_judge_fj')
def handle_judge_fj(data):
    """Judge Final Jeopardy answers - Awards points based on CSV value"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        results = data.get('results', {})  # {player_name: True/False}
        
        # Mark correct answers and award points
        for player_name, is_correct in results.items():
            if player_name in game.fj_submissions:
                game.fj_submissions[player_name]['correct'] = is_correct
                
                # Award points based on FJ value from CSV
                if is_correct and player_name in game.players:
                    game.players[player_name]['score'] += game.fj_value
        
        # Broadcast updated submissions with correct flags
        submissions = {name: {
            'answer': sub['answer'],
            'correct': sub.get('correct', False)
        } for name, sub in game.fj_submissions.items()}
        
        socketio.emit('fj_results_updated', {
            'submissions': submissions
        })
    
    broadcast_scores()
    
    # Calculate final standings with FJ results
    standings = []
    for name, p in game.players.items():
        fj_correct = game.fj_submissions.get(name, {}).get('correct', False) if game.fj_submissions else False
        standings.append({
            'name': name,
            'score': p['score'],
            'fj_correct': fj_correct
        })
    
    standings.sort(key=lambda x: x['score'], reverse=True)
    
    socketio.emit('game_complete', {'standings': standings})

@socketio.on('host_reset_game')
def handle_reset_game():
    """Reset the entire game"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        # Reset board - mark all questions as unused
        for q in game.board:
            q['used'] = False
        
        # Reset game state
        game.game_started = False
        game.current_question = None
        game.question_revealed = False
        game.buzzing_open = False
        game.buzzer_queue = []
        game.current_selector = None
        game.answer_judged = False
        game.player_results = {}
        game.show_answer = False
        game.fj_active = False
        game.fj_question_revealed = False
        game.fj_submissions = {}
        
        # Remove disconnected players and reset scores for connected players
        players_to_remove = []
        for name, player_data in game.players.items():
            if not player_data.get('connected', False):
                players_to_remove.append(name)
            else:
                # Reset score for connected players
                player_data['score'] = 0
        
        # Remove disconnected players
        for name in players_to_remove:
            del game.players[name]
    
    broadcast_game_state()
    broadcast_scores()  # Ensure players see their reset scores

@socketio.on('host_update_settings')
def handle_update_settings(data):
    """Update game settings"""
    with game.lock:
        if request.sid != game.host_socket_id:
            return
        
        if 'fj_enabled' in data:
            game.fj_enabled = data['fj_enabled']
        if 'fj_value' in data:
            game.fj_value = data['fj_value']
        if 'debug_mode' in data:
            game.debug_mode = data['debug_mode']
    
    emit('settings_updated', {'success': True})

# ============================================================================
# SOCKETIO EVENTS - PLAYER
# ============================================================================

@socketio.on('player_join')
def handle_player_join(data):
    """Player joins the game"""
    with game.lock:
        player_name = data.get('name', '').strip()
        
        if not player_name:
            emit('join_failed', {'message': 'Name cannot be empty'})
            return
        
        # Check max players
        if len(game.players) >= 30 and player_name not in game.players:
            emit('join_failed', {'message': 'Game is full (30 players max)'})
            return
        
        # Check if reconnecting
        if player_name in game.players:
            # Reconnection - reclaim identity
            game.players[player_name]['socket_id'] = request.sid
            game.players[player_name]['connected'] = True
            game.players[player_name]['last_seen'] = time.time()
            
            emit('join_success', {
                'name': player_name,
                'score': game.players[player_name]['score'],
                'reconnected': True
            })
        else:
            # New player
            game.players[player_name] = {
                'score': 0,
                'socket_id': request.sid,
                'connected': True,
                'last_seen': time.time()
            }
            
            emit('join_success', {
                'name': player_name,
                'score': 0,
                'reconnected': False
            })
        
        join_room('players')
    
    broadcast_game_state()

@socketio.on('player_buzz')
def handle_player_buzz(data):
    """Player buzzes in - CRITICAL RACE CONDITION HANDLING"""
    with game.lock:
        if not game.buzzing_open:
            emit('buzz_failed', {'message': 'Buzzing is not open'})
            return
        
        player_name = data.get('name')
        
        if not player_name or player_name not in game.players:
            emit('buzz_failed', {'message': 'Invalid player'})
            return
        
        # Check if already in queue (prevent duplicate buzzes)
        if any(b['player'] == player_name for b in game.buzzer_queue):
            emit('buzz_failed', {'message': 'Already in queue'})
            return
        
        # Add to queue with timestamp (microsecond precision)
        timestamp = time.time()
        game.buzzer_queue.append({
            'player': player_name,
            'timestamp': timestamp
        })
        
        # Sort queue by timestamp (deterministic ordering)
        game.buzzer_queue.sort(key=lambda x: x['timestamp'])
        
        # Confirm buzz to player
        position = next(i for i, b in enumerate(game.buzzer_queue) if b['player'] == player_name) + 1
        emit('buzz_confirmed', {'position': position})
    
    # Broadcast updated queue
    socketio.emit('buzzer_queue_updated', {
        'queue': [b['player'] for b in game.buzzer_queue]
    })

@socketio.on('player_submit_fj')
def handle_fj_submission(data):
    """Player submits Final Jeopardy answer - NO WAGERS"""
    with game.lock:
        if not game.fj_active:
            emit('fj_submission_failed', {'message': 'Final Jeopardy not active'})
            return
        
        player_name = data.get('name')
        answer = data.get('answer', '').strip()
        
        if player_name not in game.players:
            emit('fj_submission_failed', {'message': 'Invalid player'})
            return
        
        # Store submission with no wager (wager = 0)
        game.fj_submissions[player_name] = {
            'answer': answer,
            'wager': 0,
            'correct': False  # Track if marked correct
        }
        
        emit('fj_submission_confirmed', {})
    
    # Broadcast to TV that this player submitted (name only, no answer yet)
    socketio.emit('fj_player_submitted', {
        'player': player_name
    })
    
    # Notify host of submission count
    with game.lock:
        submission_count = len(game.fj_submissions)
        player_count = len(game.players)
    
    socketio.emit('fj_submission_count', {
        'count': submission_count,
        'total': player_count
    }, room='host')

# ============================================================================
# SOCKETIO EVENTS - CONNECTION
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    if game.debug_mode:
        print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    with game.lock:
        # Check if host
        if request.sid == game.host_socket_id:
            game.host_connected = False
            game.host_socket_id = None
            if game.debug_mode:
                print("Host disconnected")
            return
        
        # Check if player
        for player_name, player_data in game.players.items():
            if player_data['socket_id'] == request.sid:
                player_data['connected'] = False
                player_data['last_seen'] = time.time()
                if game.debug_mode:
                    print(f"Player disconnected: {player_name}")
                break
    
    broadcast_game_state()

# ============================================================================
# DEBUG MODE ENDPOINTS
# ============================================================================

@socketio.on('debug_simulate_players')
def handle_debug_simulate_players(data):
    """Debug: Simulate fake players"""
    with game.lock:
        if not game.debug_mode or request.sid != game.host_socket_id:
            return
        
        count = data.get('count', 5)
        for i in range(count):
            player_name = f"TestPlayer{i+1}"
            if player_name not in game.players:
                game.players[player_name] = {
                    'score': 0,
                    'socket_id': f'debug_{i}',
                    'connected': True,
                    'last_seen': time.time()
                }
    
    broadcast_game_state()

@socketio.on('debug_trigger_buzz')
def handle_debug_buzz(data):
    """Debug: Trigger buzz from fake player"""
    with game.lock:
        if not game.debug_mode or request.sid != game.host_socket_id:
            return
        
        if not game.buzzing_open:
            return
        
        player_name = data.get('player')
        if player_name not in game.players:
            return
        
        if not any(b['player'] == player_name for b in game.buzzer_queue):
            timestamp = time.time()
            game.buzzer_queue.append({
                'player': player_name,
                'timestamp': timestamp
            })
            game.buzzer_queue.sort(key=lambda x: x['timestamp'])
    
    socketio.emit('buzzer_queue_updated', {
        'queue': [b['player'] for b in game.buzzer_queue]
    })

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Load CSV on startup
    csv_path = 'game.csv'
    if os.path.exists(csv_path):
        success, message = load_csv(csv_path)
        print(f"CSV Load: {message}")
    else:
        print(f"Warning: {csv_path} not found. Please create it.")
    
    print(f"\n{'='*60}")
    print(f"Jeopardy Game Server Starting")
    print(f"{'='*60}")
    print(f"Local IP: {get_local_ip()}")
    print(f"Port: 5000")
    print(f"\nAccess URLs:")
    print(f"  TV Display:  http://{get_local_ip()}:5000/")
    print(f"  Host Panel:  http://{get_local_ip()}:5000/host")
    print(f"  Player Join: http://{get_local_ip()}:5000/player")
    print(f"{'='*60}\n")
    
    # Auto-open TV display in browser
    import webbrowser
    import threading
    def open_browser():
        import time
        time.sleep(1.5)  # Wait for server to start
        webbrowser.open(f'http://127.0.0.1:5000/')
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Use gevent for Python 3.12+ compatibility
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True, log_output=False)
