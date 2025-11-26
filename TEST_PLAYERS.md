# 🤖 Player Simulator - Testing Guide

## 📋 What Is This?

A test program that simulates **30 players** joining your Jeopardy game and automatically buzzing in. Perfect for testing the game with a full audience without needing 30 real people!

---

## 🚀 Quick Start

### Windows
```bash
1. Start the game server: launch.bat
2. In another window: test_players.bat
3. Watch 30 players connect!
```

### Mac/Linux
```bash
1. Start the game server: ./launch.sh
2. In another terminal: ./test_players.sh
3. Watch 30 players connect!
```

---

## 🎯 What the Simulator Does:

**1. Creates 30 Player Bots:**
```
Alice, Bob, Charlie, Diana, Eve,
Frank, Grace, Henry, Iris, Jack,
Kate, Liam, Maya, Noah, Olivia,
Paul, Quinn, Rachel, Sam, Tina,
Uma, Victor, Wendy, Xander, Yara,
Zack, Amy, Ben, Cara, Dan, Ella
```

**2. Connects All to Server:**
```
Each bot connects via SocketIO
Registers with their name
Waits for buzzing to open
```

**3. Auto-Buzzes When Ready:**
```
Host opens buzzing
  ↓
Random delay (0.1 - 2.0 seconds)
  ↓
Each bot buzzes in
  ↓
All 30 players in buzzer queue!
```

**4. Submits Final Jeopardy Answers:**
```
FJ question revealed
  ↓
Random delay (5 - 20 seconds)
  ↓
Each bot submits random answer
  ↓
All 30 answers submitted!
```

**Example FJ Answers:**
- "Who is Napoleon Bonaparte?"
- "What is the Theory of Relativity?"
- "Uhhh... Bob?"
- "I have no idea"
- "42"
- "What is love? Baby don't hurt me"

---

## 📊 What You'll See

### Console Output:
```
========================================
JEOPARDY GAME - PLAYER SIMULATOR
========================================
Server: http://localhost:5000
Players: 30
Buzz delay: 0.1-2.0s
========================================

Creating 30 player bots...
[Alice] Connected to server
[Alice] ✓ Registered successfully
[Bob] Connected to server
[Bob] ✓ Registered successfully
...

========================================
Connection Results:
  Connected: 30/30
  Registered: 30/30
========================================

SIMULATION RUNNING
Players are connected and ready to buzz!

[Alice] Buzzing opened!
[Bob] Buzzing opened!
[Alice] 🔔 BUZZED IN at position #1
[Charlie] 🔔 BUZZED IN at position #2
[Bob] 🔔 BUZZED IN at position #3
...
[Alice] ✓ CORRECT! +$3
```

### On Host Panel:
- Player count: 30
- All names visible in player list
- Buzzer queue fills up instantly
- Can judge each player

### On TV Display:
- Scoreboard shows all 30 players
- Names and scores update live
- Buzzer queue displays

---

## 🔧 Configuration

### Change Number of Players:

**Option 1: Interactive**
```bash
python test_players.py
# Prompts: "Number of players to simulate (default 30):"
# Enter: 10, 20, 50, etc.
```

**Option 2: Edit Script**
```python
# In test_players.py, line 13:
NUM_PLAYERS = 50  # Change to any number
```

### Change Buzz Speed:

```python
# In test_players.py, lines 14-15:
BUZZ_DELAY_MIN = 0.1  # Faster
BUZZ_DELAY_MAX = 2.0  # Slower

# For instant buzzing:
BUZZ_DELAY_MIN = 0.01
BUZZ_DELAY_MAX = 0.05

# For slower buzzing:
BUZZ_DELAY_MIN = 1.0
BUZZ_DELAY_MAX = 5.0
```

### Change Player Names:

```python
# In test_players.py, line 17:
PLAYER_NAMES = [
    "YourName1", "YourName2", "YourName3", ...
]
```

### Change Server URL:

```python
# In test_players.py, line 12:
SERVER_URL = 'http://192.168.1.100:5000'  # Remote server
```

---

## 📋 Testing Scenarios

### Test 1: Connection Load
```
Purpose: Can server handle 30 simultaneous connections?

Steps:
1. Start server
2. Run test_players.py
3. Check: All 30 connect and register
4. Check: No crashes or errors
```

### Test 2: Buzzer Queue
```
Purpose: Does buzzer queue handle 30 players?

Steps:
1. Start game
2. Run test_players.py
3. Select question
4. Open buzzing
5. Watch all 30 buzz in
6. Check: All show in queue with positions
7. Check: Can scroll through all players
```

### Test 3: Judging Performance
```
Purpose: Can host judge all 30 players?

Steps:
1. All 30 players buzzed in
2. Judge first player correct
3. Check: Score updates
4. Check: Player marked in queue
5. Try judging multiple players
6. Check: No duplicate points
```

### Test 4: Scoreboard Display
```
Purpose: Does scoreboard handle 30 players?

Steps:
1. 30 players connected
2. Check TV scoreboard
3. Can you see/scroll all 30?
4. Update scores
5. Check: Sorts correctly by score
```

### Test 5: Final Jeopardy
```
Purpose: Can all 30 submit FJ answers?

Note: Simulator doesn't auto-submit FJ answers
This needs to be added if you want to test FJ
```

---

## 🐛 Troubleshooting

### "Connection refused"
```
Problem: Can't connect to server

Solution:
1. Make sure server is running (launch.bat)
2. Check server URL in test_players.py
3. Verify port 5000 is correct
```

### "Module not found: socketio"
```
Problem: python-socketio not installed

Solution:
pip install python-socketio
# Or: pip3 install python-socketio
```

### Some Players Don't Connect
```
Problem: Only 25/30 connect

Possible causes:
1. Server connection limit
2. Network issues
3. Too fast connection rate

Solution:
# Increase delay in test_players.py:
time.sleep(0.2)  # Line 152, was 0.1
```

### Players Don't Buzz
```
Problem: Buzzing opened but bots don't buzz

Check:
1. Console shows "Buzzing opened!"?
2. Check buzz delay settings
3. Try manual buzz: bot.buzz() in console
```

### Console Spam
```
Problem: Too much output, can't read

Solution:
# Comment out verbose prints in test_players.py:
# print(f"[{self.name}] Connected to server")
```

---

## 🎯 Advanced Usage

### Custom Bot Behavior:

**Add FJ Answer Submission:**
```python
@self.sio.on('final_jeopardy_question_revealed')
def on_fj_question(data):
    # Wait random time
    time.sleep(random.uniform(5, 15))
    # Submit random answer
    answer = random.choice(['Paris', 'London', 'Berlin'])
    self.sio.emit('submit_final_jeopardy', {
        'name': self.name,
        'answer': answer,
        'wager': 5
    })
```

**Add Smart Buzzing** (faster for better players):
```python
def buzz(self):
    # Simulate skill level
    skill = random.random()
    if skill > 0.7:  # 30% are fast
        delay = random.uniform(0.05, 0.3)
    else:  # 70% are slower
        delay = random.uniform(0.5, 2.0)
    
    time.sleep(delay)
    self.sio.emit('player_buzz', {'name': self.name})
```

**Add Reconnection Testing:**
```python
def random_disconnect(self):
    """Randomly disconnect and reconnect"""
    while True:
        time.sleep(random.uniform(30, 120))
        if random.random() < 0.1:  # 10% chance
            print(f"[{self.name}] Simulating disconnect...")
            self.sio.disconnect()
            time.sleep(2)
            self.sio.connect(SERVER_URL)
```

---

## 📊 Performance Metrics

### What to Monitor:

**Server Console:**
```
- CPU usage
- Memory usage
- Response time
- Error messages
```

**Network:**
```
- Bandwidth usage
- Latency
- Dropped connections
```

**Browser (TV Display):**
```
- FPS / smoothness
- DOM elements (inspect)
- Memory usage
- Rendering performance
```

---

## 🔒 Limitations

### What Simulator CAN'T Do:
- ❌ Submit Final Jeopardy answers (yet)
- ❌ Answer questions with text
- ❌ Handle complex user interactions
- ❌ Simulate mobile vs desktop browsers
- ❌ Test UI rendering performance

### What Simulator CAN Do:
- ✅ Test connection capacity
- ✅ Test buzzer system
- ✅ Test scoring system
- ✅ Stress test server
- ✅ Validate player limits

---

## 📦 Files Included

```
test_players.py      - Main simulator script
test_players.bat     - Windows launcher
test_players.sh      - Mac/Linux launcher
TEST_PLAYERS.md      - This documentation
```

---

## 💡 Pro Tips

### Tip 1: Use Two Monitors
```
Monitor 1: Run simulator + console
Monitor 2: Host panel + TV display
See everything at once!
```

### Tip 2: Save Test Logs
```bash
python test_players.py > test_log.txt 2>&1
# Review logs later
```

### Tip 3: Gradual Load Testing
```
Test 1: 5 players
Test 2: 10 players
Test 3: 20 players
Test 4: 30 players
Find breaking point!
```

### Tip 4: Network Testing
```
Run simulator on different computer
Same network as server
Tests real network conditions
```

---

## 🟢 Expected Results

### Good Performance:
- ✅ All 30 connect in < 5 seconds
- ✅ All 30 register successfully
- ✅ Buzzer queue loads instantly
- ✅ No lag on TV display
- ✅ Smooth scrolling
- ✅ No dropped connections

### Potential Issues:
- ⚠️ Some players don't connect (network limit)
- ⚠️ Buzzer queue lag with all 30 (UI performance)
- ⚠️ TV scoreboard slow to render (DOM size)
- ⚠️ High CPU usage on server (SocketIO overhead)

---

**Use this to test your game before the big event!** 🎮✨
