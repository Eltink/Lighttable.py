# Ajudante - Photo Culling Tool

A lightning-fast, Lightroom-style photo culling tool built with Python and Tkinter. 

"Ajudante" is designed for photographers who need to rapidly work through thousands of frames per session. It focuses on aggressive preloading and EXIF-aware smart bracket handling to make the culling process as seamless and fast as possible.

## Features

* **Rapid Fullscreen Culling**: Walk through a source directory of JPG/HEIC/PNG images fullscreen, one at a time.
* **Smart Bracket Handling**: Automatically detects bracketed shots (using EXIF data) and hides redundant frames, allowing you to only review the best exposure of a bracketed sequence.
* **Aggressive Preloading**: Images are aggressively cached and preloaded in the background so there's no waiting between keypresses.
* **RAW File Synchronization**: An optional second stage ("Ajudante") copies the matching RAW (`.ARW`) files for your "keepers" from a separate database directory into a designated selections folder.
* **Clipboard Pathing**: Simply copy a folder path to your clipboard before launching, and the app will automatically open that folder.

## Installation

1. Ensure you have Python installed.
2. Install the required dependencies:

```bash
pip install Pillow pillow-heif imageio matplotlib
```

## Usage

You can run the tools directly using Python. Make sure to launch with `pythonw` or `python` depending on if you want the console to appear.

```bash
# Primary culling GUI
python main.pyw

# Standalone RAW-copier (also can be launched from within main.pyw via Ctrl+S)
python Ajudante.py

# Separate standalone EXIF viewer
python EXIF_reader.pyw
```

**Starting a Culling Session:**
1. Copy the path to your source folder to your clipboard.
2. Run `python main.pyw`. 
3. If no path is in your clipboard, a folder picker will open automatically.

The tool will display images fullscreen. Use your keyboard to navigate and select the "keepers", which will be copied to a `<source> sel` folder. 

## Key Bindings

| Key | Action |
| --- | --- |
| **Up** or **8** | Copy current file to the "Keepers" folder |
| **Left** / **Right** (or **4** / **6**) | Navigate Previous / Next |
| **i** | Toggle metadata info overlay |
| **s** | Toggle slideshow mode |
| **l** or **L** | Bulk preload images into cache |
| **Ctrl + S** | Launch "Ajudante" step (RAW copier) |
| **Ctrl + H** | Display histogram for the current image |
| **Ctrl + G** | Go-to specific image index |
| **Ctrl + X** | Copy current file to the "Rejected" (`<source> anti sel`) folder |
| **Ctrl + R** | Open current file's location in File Explorer |
| **Ctrl + E** | Open current file with default system Photos app |

## Architecture Overview

* **`main.pyw`**: The core culling graphical interface. It handles key bindings, the image cache, and rendering.
* **`tools.py`**: Contains the smart bracket logic and EXIF extraction tools. `is_it_showable()` is the core function that decides which frames in a bracket group are worth showing.
* **`Ajudante.py`**: The RAW-copy utility. Given a folder of selected JPGs, it finds the matching RAW files in your main photo library / database and copies them over.
* **`EXIF_reader.pyw`**: A standalone tool for exploring image EXIF data.

## Notes

* **Language**: Some variable names and functions are in Portuguese (e.g., `copiar`, `mostra_imagem`, `ajudante`). 
* **Design Philosophy**: The tool prioritizes speed over clean code. EXIF caching is intentionally memory-heavy to minimize disk I/O during rapid culling.
