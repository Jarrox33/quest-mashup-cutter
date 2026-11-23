# quest-mashup-cutter
Standalone Beat Saber section cutter, 2-song mashup builder, and random Shaffuru Medley generator for Meta Quest using Termux, Python, and ffmpeg—creates playable custom maps with no PC.
# Quest Beat Saber Mashup & Shaffuru Medley Cutter (`mashup_cutter.py`)

Slice out practice sections, stitch two maps together into a custom mashup, or generate a **random multi-song Shaffuru Medley** directly on your Meta Quest headset using **Termux**, **Python**, and **`ffmpeg`**—no PC required.

## Modes
1. **Single Song Section Cut:** Extract any start/end timestamp slice of a map with full scoring enabled.
2. **2-Song Custom Mashup:** Splice two custom songs back-to-back with automatic BPM clock synchronization.
3. **Auto Random Shaffuru Medley:** Pick how many random songs and seconds per slice—automatically stitches random map drops together and writes the full timestamp setlist into the song subtitle.

## Prerequisites
* **Beat Saber** modded with **SongCore**
* **Termux** + **Hacker's Keyboard** (enabled in Android Language & Input settings so **Enter** works)
* **Python**, **`wheel` / `setuptools`**, and **`ffmpeg`** installed in Termux

## Setup & Run
1. Install Python, `ffmpeg`, and build tools in Termux:
   ```bash
   termux-setup-storage
   pkg update -y && pkg install -y python ffmpeg
   pip install --upgrade pip setuptools wheel

2. Download mashup_cutter.py from the Releases page into /sdcard/Download and run:bash
python /sdcard/Download/mashup_cutter.py
   
3. Pick Mode 1, 2, or 3 and follow the prompts—the new map appears automatically in your Custom Levels tab!
