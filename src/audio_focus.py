import subprocess
from pydbus import SessionBus
import time
import re

def pause_spotify(bus):
    try: 
        spotify = bus.get("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
        spotify.Pause()
        print("[SeamlessAudio] Paused Spotify")
        return True
    except Exception as e: 
        # Spotify may not be running
        print(f"[SeamlessAudio] Could not pause Spotify: {e}")
        return False
    
def play_spotify(bus):
    try:
        spotify = bus.get("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
        spotify.Play()
        print("[SeamlessAudio] Resumed Spotify")
        return True
    except Exception as e:
        # Spotify may not be running
        print(f"[SeamlessAudio] Could not resume Spotify: {e}")
        return False

def is_spotify_playing(bus):
    """Check if Spotify is currently playing"""
    try:
        spotify = bus.get("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
        status = spotify.PlaybackStatus
        return status == "Playing"
    except Exception:
        return False

def get_active_non_spotify_streams():
    """Get all currently active non-Spotify audio streams"""
    try:
        sink_inputs = subprocess.check_output(["pactl", "list", "sink-inputs"], text=True)
        active_streams = set()
        current_id = None
        is_playing = False
        is_spotify = False
        
        for line in sink_inputs.splitlines():
            line = line.strip()
            
            if line.startswith("Sink Input #"):
                # Save previous stream if it was active and not Spotify
                if current_id is not None and is_playing and not is_spotify:
                    active_streams.add(current_id)
                
                # Start tracking new stream
                current_id = int(line.split('#')[1])
                is_playing = True  # Default to playing
                is_spotify = False
                
            elif "Corked:" in line:
                # Stream is paused if corked=yes
                is_playing = "no" in line.lower()
                
            elif "application.name" in line and "spotify" in line.lower():
                is_spotify = True
        
        # Don't forget the last stream
        if current_id is not None and is_playing and not is_spotify:
            active_streams.add(current_id)
            
        return active_streams
        
    except subprocess.CalledProcessError as e:
        print(f"[SeamlessAudio] Error getting sink inputs: {e}")
        return set()

def parse_pactl_event(line):
    """Parse a pactl subscribe event line"""
    # Example: "Event 'new' on sink-input #123"
    # Example: "Event 'remove' on sink-input #123"
    match = re.search(r"Event '(\w+)' on sink-input #(\d+)", line)
    if match:
        event_type = match.group(1)
        sink_id = int(match.group(2))
        return event_type, sink_id
    return None, None

def main():
    bus = SessionBus()
    
    # Get initial states
    active_others = get_active_non_spotify_streams()
    spotify_was_playing = is_spotify_playing(bus)
    
    print(f"[SeamlessAudio] Starting with {len(active_others)} active non-Spotify streams")
    print(f"[SeamlessAudio] Spotify initially {'playing' if spotify_was_playing else 'paused'}")
    
    try:
        proc = subprocess.Popen(["pactl", "subscribe"], stdout=subprocess.PIPE, text=True, bufsize=1)
        print("[SeamlessAudio] Listening for audio stream events...")
        
        for line in proc.stdout:
            line = line.strip()
            
            if "sink-input" in line:
                event_type, sink_id = parse_pactl_event(line)
                
                if event_type and sink_id is not None:
                    print(f"[SeamlessAudio] Audio event: {event_type} sink #{sink_id}")
                    
                    # Update our active streams based on actual state
                    active_others = get_active_non_spotify_streams()
                    current_spotify_playing = is_spotify_playing(bus)
                    
                    # Logic: pause Spotify if other streams are active and Spotify is playing
                    if active_others and current_spotify_playing:
                        if pause_spotify(bus):
                            spotify_was_playing = True
                    
                    # Logic: resume Spotify if no other streams and we paused it
                    elif not active_others and spotify_was_playing and not current_spotify_playing:
                        play_spotify(bus)
                        spotify_was_playing = False
                
                # Small delay to avoid rapid state changes
                time.sleep(0.1)

  #Exception handling
    except KeyboardInterrupt:
        print("\n[SeamlessAudio] Shutting down...")
    except Exception as e:
        print(f"[SeamlessAudio] Unexpected error: {e}")
    finally:
        if 'proc' is not None():
            proc.terminate()

if __name__ == "__main__":
    main()
