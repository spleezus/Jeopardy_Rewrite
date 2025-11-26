# 🎮 Jeopardy Game - Complete Package

A full-featured Jeopardy game system supporting 20-30 simultaneous players with host control, TV display, and player interfaces.

## 🚀 Quick Start

### Windows
```
Double-click launch.bat
```

### Mac/Linux
```bash
chmod +x launch.sh
./launch.sh
```

OR manually:
```bash
pip3 install -r requirements.txt
python3 server.py
```

## 📋 Requirements

- **Python 3.8+** (3.12+ recommended)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for initial package installation)

## 🖥️ Platform-Specific Instructions

### Windows

1. Extract the ZIP file
2. Double-click `launch.bat`
3. Browser opens automatically to TV display
4. Navigate to `/host` for host controls
5. Share `/player` URL with players

**Troubleshooting:**
- If Python not found: Install from https://python.org/downloads/
- Check "Add Python to PATH" during installation
- Restart computer after installing Python

### macOS

1. Extract the ZIP file
2. Open Terminal
3. Navigate to folder: `cd /path/to/jeopardy-FINAL-POLISHED`
4. Make launcher executable: `chmod +x launch.sh`
5. Run: `./launch.sh`

**Troubleshooting:**
- Install Python 3: `brew install python3`
- If Homebrew not installed: https://brew.sh/
- Allow terminal access in System Preferences > Security

### Linux

1. Extract the ZIP file
2. Open Terminal
3. Navigate to folder: `cd /path/to/jeopardy-FINAL-POLISHED`
4. Make launcher executable: `chmod +x launch.sh`
5. Run: `./launch.sh`

**Troubleshooting:**
- Ubuntu/Debian: `sudo apt install python3 python3-pip`
- Fedora: `sudo dnf install python3 python3-pip`
- Arch: `sudo pacman -S python python-pip`

## 🌐 Accessing the Game

Once the server starts, you'll see:

```
============================================================
Jeopardy Game Server Starting
============================================================
Local IP: 192.168.1.100
Port: 5000

Access URLs:
  TV Display:  http://192.168.1.100:5000/
  Host Panel:  http://192.168.1.100:5000/host
  Player Join: http://192.168.1.100:5000/player
============================================================
```

### On Same Computer:
- TV Display: http://localhost:5000/
- Host Panel: http://localhost:5000/host
- Player Join: http://localhost:5000/player

### On Network (Other Devices):
- Use the IP address shown (e.g., http://192.168.1.100:5000/)
- Players on same WiFi can join
- Display TV on large screen/projector

## 📝 CSV File Format

The `game.csv` file defines your game content:

```csv
Game Title:,Jeopardy Test Game
Host Password,host123

Basic Jeopardy
,Science,History,Pop Culture,Geography,Sports
Question|Answer,Question|Answer,Question|Answer,Question|Answer,Question|Answer
Question|Answer,Question|Answer,Question|Answer,Question|Answer,Question|Answer
...
Final Jeopardy
Question|Answer,10
```

**Encoding Support:**
- ✅ UTF-8 (standard)
- ✅ Windows-1252 (Excel default)
- ✅ Smart quotes and special characters

## 🎮 Features

### Complete Game Flow
- Category reveal animation
- 25 regular questions ($1-$5)
- Buzzer system with queue
- Live scoring
- Final Jeopardy
- Final leaderboard with stars for FJ winners

### Host Controls
- Start/pause game
- Select questions
- Open/close buzzing
- Judge answers (correct/incorrect)
- Jump to Final Jeopardy
- Show FJ question when ready
- Live judging with instant feedback
- Reset game

### Player Experience
- Register with name
- See current question
- Buzz in button
- Position in queue
- Score tracking
- Final Jeopardy submission
- Visual feedback (✓/✗)

### TV Display
- Full game board
- Category reveal animation
- Active question display
- Live scoreboard
- Buzzer queue with results
- Final Jeopardy question
- Final leaderboard

## 🔧 Advanced Options

### Change Port
Edit `server.py`, line ~900:
```python
socketio.run(app, host='0.0.0.0', port=5000, ...)
```
Change `5000` to your desired port.

### Disable Auto-Open Browser
Edit `server.py`, remove/comment out lines ~892-896:
```python
# def open_browser():
#     import time
#     time.sleep(1.5)
#     webbrowser.open(f'http://127.0.0.1:5000/')
# threading.Thread(target=open_browser, daemon=True).start()
```

### Build Standalone Executable

**Windows:**
```bash
build.bat
```

**Mac/Linux:**
```bash
chmod +x build.sh
./build.sh
```

Creates executable in `dist/` folder - no Python required to run!

## 📦 Package Contents

```
jeopardy-FINAL-POLISHED/
├── launch.bat          # Windows launcher
├── launch.sh           # Mac/Linux launcher
├── server.py           # Main server
├── game.csv            # Sample game data
├── requirements.txt    # Python packages
├── build.bat          # Windows executable builder
├── build.sh           # Mac/Linux executable builder
└── templates/
    ├── tv.html        # TV display
    ├── host.html      # Host control panel
    └── player.html    # Player interface
```

## 🐛 Troubleshooting

### Port Already in Use
```
Error: Address already in use
```
**Solution:** 
- Close other programs using port 5000
- Or change port in server.py

### CSV Won't Load
```
UnicodeDecodeError: 'utf-8' codec can't decode...
```
**Solution:** Already fixed! Automatic encoding fallback handles this.

### Can't Connect from Other Devices
**Check:**
1. Firewall allows port 5000
2. All devices on same network
3. Using correct IP address (not localhost)

### Python Not Found (Windows)
**Solution:**
1. Install Python from https://python.org
2. Check "Add Python to PATH"
3. Restart computer
4. Try again

### Permission Denied (Mac/Linux)
```
Permission denied: './launch.sh'
```
**Solution:**
```bash
chmod +x launch.sh
./launch.sh
```

## 📖 How to Play

1. **Setup:**
   - Start server with launcher
   - Open TV display on projector/screen
   - Host opens host panel
   - Players visit player URL on phones

2. **Game Start:**
   - Host clicks "Start Game"
   - Categories reveal one by one
   - Host selects first question

3. **Playing Questions:**
   - Host selects question
   - Question appears on TV (dimmed)
   - Host reads question aloud
   - Host clicks "Open Buzzing"
   - Players buzz in
   - First player answers
   - Host marks correct/incorrect
   - First correct player gets points

4. **Final Jeopardy:**
   - After 25 questions (or Jump to FJ)
   - Host clicks "Start Final Jeopardy"
   - Host sees question first
   - Host clicks "Show Question to Players & TV"
   - Players submit answers
   - Host clicks "Reveal All Answers"
   - Host judges each player
   - Host clicks "Complete Game"
   - Final leaderboard appears

## 🏆 Scoring

- Questions: $1, $2, $3, $4, $5
- Only first correct answer gets points
- No point deduction for wrong answers
- Final Jeopardy: Custom value (from CSV)
- Stars (⭐) show FJ winners on leaderboard

## 🎨 Customization

### Change Game Name
Edit `game.csv`, first line:
```csv
Game Title:,Your Custom Name
```

### Change Host Password
Edit `game.csv`, second line:
```csv
Host Password,yourpassword
```

### Modify Questions
Edit `game.csv` - see format above

### Change Colors/Styling
Edit template files in `templates/` folder (HTML/CSS)

## 📄 License

Free to use for educational and entertainment purposes.

## 🙋 Support

If you encounter issues:
1. Check troubleshooting section above
2. Verify Python and packages installed
3. Check firewall settings
4. Ensure CSV file properly formatted

---

**Enjoy your Jeopardy game!** 🎮✨
