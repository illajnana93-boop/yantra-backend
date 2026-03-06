import wave
import numpy as np
import os
import glob

def check_audio_health():
    files = glob.glob("static/audio/guruji_response_*.wav")
    if not files:
        print("No audio files found.")
        return
    
    latest_file = max(files, key=os.path.getmtime)
    print(f"Checking latest file: {latest_file}")
    
    try:
        with wave.open(latest_file, 'rb') as w:
            params = w.getparams()
            print(f"Params: {params}")
            frames = w.readframes(params.nframes)
            data = np.frombuffer(frames, dtype=np.int16)
            peak = np.abs(data).max()
            mean = np.abs(data).mean()
            print(f"Peak Amplitude: {peak}")
            print(f"Mean Amplitude: {mean}")
            if peak == 0:
                print("🚨 SILENT AUDIO DETECTED!")
            elif peak < 100:
                print("⚠️ VERY QUIET AUDIO DETECTED!")
            else:
                print("✅ Audio seems healthy (Signal detected)")
    except Exception as e:
        print(f"Error checking: {e}")

if __name__ == "__main__":
    check_audio_health()
