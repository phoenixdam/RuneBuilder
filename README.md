# League of Legends Champion Rune Builder

A desktop application for creating and managing League of Legends rune pages with champion-specific builds.

## Requirements

### System Requirements

- **Windows 10/11** (for .bat scripts)
- **Python 3.7+** with pip

### Python Dependencies

- **Pillow (PIL)** - For image processing
- **tkinter** - GUI framework (usually included with Python)
- **sqlite3** - Database (included with Python)

## Quick Start

### Option 1: Automatic Setup (Recommended)

1. Double-click `setup_and_run.bat`
2. The script will:
   - Check if Python is installed
   - Install required dependencies
   - Launch the application

### Option 2: Manual Setup

1. Open Command Prompt in the RuneBuilder folder
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python champion_rune_builder.py
   ```

### Option 3: Simple Run (if already set up)

1. Double-click `run_rune_builder.bat`

## Installation Guide

### If Python is not installed:

1. Go to [python.org](https://python.org)
2. Download Python 3.7+ for Windows
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Restart your computer after installation
5. Run `setup_and_run.bat`

### If you get permission errors:

- Right-click the .bat file → "Run as administrator"

## Features

- Champion selection with search
- Primary and secondary rune tree selection
- Keystone and rune configuration
- Stat shard selection
- Save/load rune pages per champion
- Set default rune pages
- Delete unwanted rune pages
- Hover tooltips for saved rune pages

## File Structure

```
RuneBuilder/
├── champion_rune_builder.py   # Main application
├── requirements.txt           # Python dependencies
├── setup_and_run.bat         # Auto-setup launcher
├── run_rune_builder.bat      # Simple launcher
├── rune_builder.db           # SQLite database (created automatically)
├── champions_files/          # Champion images
├── runes_files/              # Rune-related images
│   ├── runes/                # Rune icons (e.g., Conqueror, Electrocute)
│   └── shards/               # Rune shard icons (e.g., Attack Speed, Armor)
└── icons/                    # UI icons
```

## 🖼️ Image Assets

This application requires local image files for champions, runes, and rune shards. You need to download and place them into the correct folders with **exact filenames** as used on the League of Legends Wiki.

### 🔹 1. Champion Icons

- **Source**:  
  [https://leagueoflegends.fandom.com/wiki/List_of_champions](https://leagueoflegends.fandom.com/wiki/List_of_champions)

- **How to Download**:  
  Right-click each champion’s image and select "Save image as...".

- **Save To**: `champions_files/`
- **Filename Format**:  
  Use the full filename as shown on the site (e.g.):
  42px-Zyra_OriginalSquare.png
  42px-Yasuo_OriginalSquare.png
  42px-Ahri_OriginalSquare.png

---

### 🔸 2. Rune Icons

- **Source**:  
  [https://leagueoflegends.fandom.com/wiki/Rune](https://leagueoflegends.fandom.com/wiki/Rune)  
  Use the rune icon table in the content (`//*[@id="mw-content-text"]/div[1]/table`)

- **How to Download**:  
  Right-click each rune icon and save.

- **Save To**: `runes_files/`
- **Filename Format**:  
  52px-Conqueror_rune.png
  52px-Electrocute_rune.png
  52px-Absolute_Focus_rune.png

---

### 🟢 3. Rune Shard Icons

- **Source**:  
  Also found in the [Rune Wiki page](https://leagueoflegends.fandom.com/wiki/Rune) under the shards section.

- **Save To**: `runes_files/` or a separate folder like `rune_shards/` if your app distinguishes them.

- **Filename Format**:  
  30px-Rune_shard_Adaptive_Force.png
  30px-Rune_shard_Armor.png
  30px-Rune_shard_Attack_Speed.png
  30px-Rune_shard_Magic_Resist.png

---

> ⚠️ **Legal Note**: All icons and artwork are property of Riot Games. These assets are provided by the community wiki and are intended for **personal, non-commercial use** only. Do not redistribute or use commercially without permission from Riot Games.

## Troubleshooting

### "Python is not installed or not in PATH"

- Install Python from python.org
- Make sure "Add Python to PATH" was checked during installation
- Restart your computer

### "Failed to install some requirements"

- Run Command Prompt as Administrator
- Try: `pip install --user Pillow`

### Application won't start

- Check that all image folders exist (champions_files, runes_files, icons)
- Ensure you have write permissions in the RuneBuilder folder

### Database errors

- Delete `rune_builder.db` to reset the database
- The application will recreate it automatically

## Support

If you encounter issues:

1. Check the Command Prompt window for error messages
2. Ensure all image folders and files are present
3. Try running as administrator
4. Restart your computer after installing Python
