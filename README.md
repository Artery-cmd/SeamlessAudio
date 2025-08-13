# SeamlessAudio

A background tool that automatically pauses one audio stream when another starts. The paused audio stream can then be set to continue if playback ends or is paused allowing for efficient and uninterrupted workflow.

## Features
- Detects new audio streams via `pactl subscribe`
- Pauses Spotify via MPRIS when another stream starts
- Extendable for multiple apps & rules
  
  ## Requirements
Python 3.8+
PulseAudio (or PipeWire in PulseAudio compatibility mode)
Apps that support MPRIS (Spotify, VLC, etc.)

## Install
```bash
git clone https://github.com/yourname/audio-focus.git
cd audio-focus
pip install -r requirements.txt
