import machine
import time
import math

# --- Setup ---
sensor = machine.ADC(27)
led = machine.Pin("LED", machine.Pin.OUT) 

MIN_BEAT_MS = 300       
last_beat_time = 0

# --- Buffers ---
BUFFER_SIZE = 400
signal_history = [0.0] * BUFFER_SIZE
history_idx = 0

# Store up to 10 beat intervals for BPM and HRV math
BPM_AVERAGE_COUNT = 10
interval_history = []

print("Starting HRM-2511B BPM & HRV Detector...")
print("PLACE YOUR FINGER ON THE SENSOR NOW.")

# --- Calibration Phase ---
for i in range(3, 0, -1):
    print(f"Calibrating in {i}...")
    time.sleep(1)

print("Reading baseline...")
baseline = sum(sensor.read_u16() for _ in range(50)) / 50

print("Calibration complete! Monitoring...")
print("-" * 60)

while True:
    # 1. Fast snapshot
    current_val = sum(sensor.read_u16() for _ in range(10)) / 10
    
    # 2. Smooth the baseline background light
    baseline = (baseline * 0.99) + (current_val * 0.01)
    
    # 3. Calculate AC signal
    pulse_signal = current_val - baseline
    
    # 4. Save to our signal dataset buffer
    signal_history[history_idx] = pulse_signal
    history_idx = (history_idx + 1) % BUFFER_SIZE
    
    # 5. Calculate dynamic threshold
    recent_max = max(signal_history)
    dynamic_threshold = max(recent_max * 0.6, 10) 
    
    current_time = time.ticks_ms()
    
    # 6. Check for Beat
    if pulse_signal > dynamic_threshold:
        if (current_time - last_beat_time) > MIN_BEAT_MS:
            
            interval = current_time - last_beat_time
            raw_bpm = 60000 / interval
            
            last_beat_time = current_time
            
            # Only process realistic human heart rates
            if 40 <= raw_bpm <= 220:
                interval_history.append(interval)
                
                if len(interval_history) > BPM_AVERAGE_COUNT:
                    interval_history.pop(0) 
                
                beats_stored = len(interval_history)
                
                # Calculate Average BPM
                avg_interval = sum(interval_history) / beats_stored
                avg_bpm = 60000 / avg_interval
                
                # Calculate HRV (RMSSD)
                rmssd = 0.0
                if beats_stored > 1:
                    # 1. Find the differences between consecutive beats
                    squared_diffs = []
                    for i in range(1, beats_stored):
                        diff = interval_history[i] - interval_history[i-1]
                        # 2. Square the differences
                        squared_diffs.append(diff * diff)
                    
                    # 3. Average the squared differences, then take the Square Root
                    mean_squared = sum(squared_diffs) / len(squared_diffs)
                    rmssd = math.sqrt(mean_squared)

                led.value(1)
                
                # Output everything cleanly
                if beats_stored > 1:
                    print(f"❤️ Avg BPM: {avg_bpm:.1f} | HRV (RMSSD): {rmssd:.1f} ms | Sig: {pulse_signal:.0f}")
                else:
                    print(f"❤️ Avg BPM: {avg_bpm:.1f} | HRV: Gathering data... | Sig: {pulse_signal:.0f}")
                
                time.sleep(0.02)
                led.value(0)

    time.sleep(0.005)