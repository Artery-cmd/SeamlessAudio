import subprocess
import re

def pauseSpotify():
  subprocess.run(["dbus-send", "--print -reply", "--dest=org.mpris.MediaPlayer2.spotify","/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player.Pause"

#Listen to PulseAudio events
proc = subprocess.Popen(["pactl", "subscribe"], stdout=subprocess.PIPE, text=True)

for line in proc.stdout:
  if "new" in line and "sink-input" in line:
    sinkInputs = subprocess.check_output(["pactl", "list", "sink-inputs"], text=True
    if "application.name = \"Spotify\"" in sinkInputs:
      pauseSpotify()
