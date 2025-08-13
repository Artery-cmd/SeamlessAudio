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

def update_active_others(active_others):
        sink_inputs = subprocess.check_output(["pactl", "list", "sink-inputs"], text=True)
        running_sinks = set()
        current_id = None
        is_playing = True
        is_spotify = False

        for line in sink_inputs.splitlines():
            line = line.strip()
            if line.startswith("Sink Input #"):
                current_id = int(line.split('#')[1])
                is_playing = True
                is_spotify = False
            elif "Corked" in line:
                is_playing = ("no" in line.lower())
            elif "application.name" in line and "spotify" in line.lower():
                is_spotify = True
            elif current_id is not None:
                if not is_spotify and is_playing:
                    running_sinks.add(current_id)
                current_id = None
        active_others.intersection_update(running_sinks) #Remove streams that are no longer running

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
              #Add new stream
              active_others.add(sink_id)
              pause_spotify(bus)  
          
        elif "remove" in line:
            #Remove ended stream
            active_others.discard(sink_id)
          
      #Update active streams
      update_active_others(active_others) 
      time.sleep(0.15)
    
      #Resume spotify if nothing is active
      if not active_others:
          play_spotify(bus)
                   
      
if __name__ == "__main__":
    main()
