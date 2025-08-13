import subprocess
from pydbus import SessionBus


def pause_spotify(bus):
  try: 
    spotify = bus.get("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    spotify.Pause()
    print("[SeamlessAudio] Paused Spotify")
  except Exception as e: 
    #Spotify may not be running
    print(f"[SeamlessAudio] Could not pause Spotify: {e}")

#Listen to PulseAudio events
def main():
  bus = SessionBus()
  proc = subprocess.Popen(["pactl", "subscribe"], stdout=subprocess.PIPE, text=True) #Holds list of processes
  print("[SeamlessAudio] Listening for new audio streams...")

  for line in proc.stdout:
    if "new" in line and "sink-input" in line:
      sink_inputs = subprocess.check_output(["pactl", "list", "sink-inputs"], text=True)
      if "application.name = \"Spotify\"" in sink_inputs:
        pause_spotify(bus)

if __name__ == "__main__":
    main()
