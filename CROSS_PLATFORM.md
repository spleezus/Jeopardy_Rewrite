# ✅ CROSS-PLATFORM VERSION - Works on Windows, Mac, and Linux!

## 📥 Download Universal Package
**[jeopardy-CROSS-PLATFORM.zip](computer:///mnt/user-data/outputs/jeopardy-CROSS-PLATFORM.zip)** (38KB)

---

## 🎯 WHAT'S NEW:

### Platform Support
- ✅ **Windows** - launch.bat (double-click)
- ✅ **Mac** - launch.sh (terminal)
- ✅ **Linux** - launch.sh (terminal)

### What's Included
- ✅ launch.bat (Windows)
- ✅ launch.sh (Mac/Linux)
- ✅ README.md (complete guide)
- ✅ All previous fixes
- ✅ Your game.csv

---

## 🚀 QUICK START:

### Windows
```
1. Extract ZIP
2. Double-click launch.bat
3. Browser opens automatically
4. Play!
```

### Mac
```bash
1. Extract ZIP
2. Open Terminal
3. cd /path/to/jeopardy-FINAL-POLISHED
4. chmod +x launch.sh
5. ./launch.sh
6. Browser opens automatically
7. Play!
```

### Linux
```bash
1. Extract ZIP
2. Open Terminal
3. cd /path/to/jeopardy-FINAL-POLISHED
4. chmod +x launch.sh
5. ./launch.sh
6. Browser opens automatically
7. Play!
```

---

## 📋 WHAT EACH LAUNCHER DOES:

### launch.bat (Windows)
- Checks Python installed
- Checks pip installed
- Installs requirements
- Starts server
- Opens browser automatically

### launch.sh (Mac/Linux)
- Checks Python 3 installed
- Checks pip3 installed
- Installs requirements (--user flag)
- Starts server
- Opens browser automatically
- Executable permission required

---

## 🔧 PLATFORM DIFFERENCES:

### Windows
- Uses: `python` and `pip`
- Packages install globally
- .bat files work natively
- Browser opens with `webbrowser`

### Mac/Linux
- Uses: `python3` and `pip3`
- Packages install to user directory (--user)
- .sh files need execute permission
- Browser opens with `webbrowser`

### Both Platforms
- Same server.py
- Same templates
- Same game logic
- Same CSV format
- Same features

---

## 🌐 NETWORKING:

### Same Computer
```
TV:     http://localhost:5000/
Host:   http://localhost:5000/host
Player: http://localhost:5000/player
```

### Multiple Devices (Same WiFi)
```
TV:     http://192.168.1.100:5000/
Host:   http://192.168.1.100:5000/host
Player: http://192.168.1.100:5000/player
```
(Use IP address shown in console)

### Works With
- ✅ Windows PCs
- ✅ MacBooks
- ✅ iPhones/iPads
- ✅ Android phones/tablets
- ✅ Linux computers
- ✅ Chromebooks
- ✅ Any device with browser

---

## 🐛 TROUBLESHOOTING:

### Windows: "Python not found"
```
Download: https://python.org/downloads/
Check: "Add Python to PATH"
Restart computer
```

### Mac: "python3 not found"
```bash
# Install Homebrew first:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install Python:
brew install python3
```

### Linux: "python3 not found"
```bash
# Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip

# Fedora:
sudo dnf install python3 python3-pip

# Arch:
sudo pacman -S python python-pip
```

### Mac/Linux: "Permission denied"
```bash
chmod +x launch.sh
./launch.sh
```

### Port 5000 Already in Use
**Option 1:** Close other programs
**Option 2:** Edit server.py, change port

### Can't Access from Phone
1. Check firewall (allow port 5000)
2. Verify same WiFi network
3. Use IP (not localhost)
4. Try disabling VPN

---

## 📦 BUILD EXECUTABLES:

### Windows Executable
```bash
build.bat
```
Creates: `dist/JeopardyGame.exe`
- No Python required on target machine
- Copy game.csv with it
- Double-click to run

### Mac/Linux Executable
```bash
chmod +x build.sh
./build.sh
```
Creates: `dist/JeopardyGame`
- No Python required on target machine
- Copy game.csv with it
- Run: `./JeopardyGame`

---

## 🎮 COMPLETE FEATURE LIST:

### Game Flow
- ✅ Category reveal animation
- ✅ 25 questions ($1-$5)
- ✅ Buzzer queue system
- ✅ Live scoring
- ✅ Final Jeopardy
- ✅ Final leaderboard with stars

### Host Controls
- ✅ Start/reset game
- ✅ Select questions
- ✅ Control buzzing
- ✅ Judge answers instantly
- ✅ Jump to Final Jeopardy
- ✅ Show FJ question when ready
- ✅ Live FJ judging

### Player Experience
- ✅ Register with name
- ✅ See questions
- ✅ Buzz in
- ✅ Track score
- ✅ Submit FJ answer
- ✅ Visual feedback (✓/✗)

### TV Display
- ✅ Game board
- ✅ Active question
- ✅ Scoreboard
- ✅ Buzzer queue
- ✅ FJ question
- ✅ Final results

---

## 📄 FILES INCLUDED:

```
jeopardy-FINAL-POLISHED/
├── README.md           # Complete guide
├── launch.bat          # Windows launcher
├── launch.sh           # Mac/Linux launcher (executable)
├── server.py           # Game server
├── game.csv            # Your game data
├── requirements.txt    # Python packages
├── build.bat          # Windows exe builder
├── build.sh           # Mac/Linux exe builder
└── templates/
    ├── tv.html        # TV display
    ├── host.html      # Host controls
    └── player.html    # Player UI
```

---

## 🟢 STATUS: UNIVERSAL

**✅ Works on Windows**
**✅ Works on Mac**
**✅ Works on Linux**
**✅ Works on mobile**
**✅ Works on tablets**
**✅ Encoding fixed**
**✅ All bugs fixed**
**✅ Complete documentation**

Perfect cross-platform compatibility! 🎮✨
