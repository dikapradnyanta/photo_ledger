# 📸 Shot Ledger

Professional Photo Data Acquisition & Management System

A minimalist desktop application for efficient photo capture with automatic Excel logging. Perfect for event photography, employee ID photos, student records, and any scenario requiring organized batch photo capture.

## ✨ Features

- **Live Camera Preview** - Smooth real-time preview from webcam/DSLR
- **Smart File Management** - Automatic folder organization by category
- **Excel Logging** - Real-time data logging with full session tracking
- **Photo Preview & Edit** - Review, edit, and navigate captured photos
- **Duplicate Handling** - Smart duplicate detection with user preferences
- **Trash System** - Soft delete with undo functionality
- **Session Management** - Export reports and manage photo sessions
- **Crash Recovery** - Auto-save session for unexpected closures
- **Keyboard Shortcuts** - SPACEBAR to capture, ENTER to confirm, etc.

## 📋 Requirements

- Windows 10/11 (64-bit)
- Python 3.10+ (for development)
- Webcam or USB camera

## 🚀 Quick Start

### For End Users (Standalone EXE)

1. Download `ShotLedger_Setup.exe`
2. Run installer
3. Launch Shot Ledger from Start Menu
4. Select project folder
5. Start capturing!

### For Developers

1. **Clone/Download the project**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📂 Project Structure

```
shot_ledger/
├── main.py                 # Application entry point
├── config.py               # Configuration manager
├── models.py               # Data models & session
├── ui/
│   ├── main_window.py      # Main UI
│   ├── folder_selector.py  # Startup dialog
│   └── preview_window.py   # Photo preview
├── utils/
│   └── camera.py           # Camera handler
├── requirements.txt        # Python dependencies
├── build.bat               # Build script (Windows)
└── README.md               # This file
```

## 🎯 Workflow

1. **Select Project Folder** - Choose where photos will be saved
2. **Configure Camera** - Select camera from dropdown
3. **Enter Information**
   - Subfolder (e.g., "Engineering", "Marketing")
   - Name (e.g., "John Doe", "EMP-001")
4. **Capture Photo** - Click button or press SPACEBAR
5. **Preview & Edit** - Review, edit details, or delete
6. **Keep & Continue** - Photo saved, ready for next person
7. **Export Report** - Save Excel report when done
8. **End Session** - Clear session data and trash

## ⌨️ Keyboard Shortcuts

### Main Window
- `SPACEBAR` - Capture photo
- `Ctrl+E` - Export report
- `Ctrl+L` - End session

### Preview Window
- `ENTER` - Keep & Continue
- `DELETE` - Delete photo
- `ESC` - Cancel
- `←` / `→` - Navigate between photos

## 📊 Excel Output Format

| Timestamp | Subfolder | Name | Filename | File Path |
|-----------|-----------|------|----------|-----------|
| 2025-01-17 14:30:00 | Engineering | John Doe | John Doe.jpg | D:\Photos\Engineering\John Doe.jpg |

## ⚙️ Configuration

Settings are stored in: `C:\Users\[Username]\AppData\Local\ShotLedger\config.json`

Key settings:
- **duplicate_handling**: "ask", "auto_increment", or "replace"
- **use_trash**: Enable soft delete with undo
- **confirm_delete**: Show confirmation dialogs
- **on_exit**: "keep_session", "end_session", or "ask"

## 🔧 Building Standalone EXE

### Using PyInstaller

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Build EXE**
   ```bash
   pyinstaller --onefile --windowed --name "ShotLedger" main.py
   ```

3. **Output**: `dist/ShotLedger.exe`

### Using Inno Setup (Installer)

1. **Download Inno Setup**: https://jrsoftware.org/isdl.php

2. **Create installer script** (`installer.iss`):
   ```iss
   [Setup]
   AppName=Shot Ledger
   AppVersion=1.0
   DefaultDirName={autopf}\ShotLedger
   DefaultGroupName=Shot Ledger
   OutputDir=Output
   OutputBaseFilename=ShotLedger_Setup
   Compression=lzma2
   SolidCompression=yes
   
   [Files]
   Source: "dist\ShotLedger.exe"; DestDir: "{app}"
   
   [Icons]
   Name: "{group}\Shot Ledger"; Filename: "{app}\ShotLedger.exe"
   Name: "{autodesktop}\Shot Ledger"; Filename: "{app}\ShotLedger.exe"
   ```

3. **Compile**: Open Inno Setup → Compile → Done!

## 🐛 Troubleshooting

### Camera Not Detected
- Ensure camera is connected
- Try different camera index (Camera 0, 1, or 2)
- For DSLR: Install manufacturer's webcam utility (Canon EOS Webcam, Sony Imaging Edge, etc.)

### Excel Permission Error
- Close Excel file if open
- Check file permissions
- Try running as Administrator

### App Won't Start
- Check Windows Event Viewer for errors
- Ensure .NET Framework is installed
- Run from command line to see error messages

## 📝 Use Cases

- **Employee Onboarding** - Capture ID photos with employee info
- **Event Registration** - Photo + data collection for conferences
- **Student ID Cards** - Batch photo capture by class
- **Medical Records** - Patient photos with metadata
- **Security/Access Control** - Building access photo database

## 🤝 Support

For issues, questions, or feature requests, please open an issue on GitHub.

## 📄 License

MIT License - Free for personal and commercial use

## 🎉 Credits

Created with:
- CustomTkinter (Modern UI)
- OpenCV (Camera handling)
- Pandas & OpenPyXL (Excel operations)

---

**Shot Ledger** - Professional photo management made simple.