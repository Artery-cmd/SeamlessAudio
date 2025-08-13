import subprocess
from pydbus import SessionBus
import time


def pause_spotify(bus):
  try: 
      spotify = bus.get("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
      spotify.Pause()
      print("[SeamlessAudio] Paused Spotify")
  except Exception as e: 
      #Spotify may not be running
      print(f"[SeamlessAudio] Could not pause Spotify: {e}")
    
def play_spotify(bus):
    try:
        spotify = bus.get("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
        spotify.Play()
        print("[SeamlessAudio] Resumed Spotify")
    except Exception as e:
        #Spotify may not be running
        print(f"[SeamlessAudio] Could not resume Spotify: {e}")

#Listen to PulseAudio events
def main():
    bus = SessionBus()
    active_others = set()
    proc = subprocess.Popen(["pactl", "subscribe"], stdout=subprocess.PIPE, text=True) #Holds list of processes
    print("[SeamlessAudio] Listening for new audio streams...")

    for line in proc.stdout:
      if "sink-input" in line:
        sink_id = int(line.split('#')[1])
        
        if "new" in line:
          try:
              sink_inputs = subprocess.check_output(["pactl", "list", "sink-inputs"], text=True)
          except Exception as e: 
              print(f"[SeamlessAudio] Could not access audio inputs: {e}")
          
          if 'application.name = "Spotify"' not in sink_inputs:
              #Add new stream
              active_others.add(sink_id)
              pause_spotify(bus)
              time.sleep(0.05)  
          
        elif "remove" in line:
            #Remove ended stream
            active_others.discard(sink_id)
            if not active_others:
                play_spotify(bus)
                time.sleep(0.05)
      
if __name__ == "__main__":
    main()
