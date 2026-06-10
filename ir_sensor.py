import machine
import time

# --- Setup ---
# ADC on Pin 28 (GP28)
sensor = machine.ADC(27)
# Internal LED on the Pico (GP25 or 'LED' for Pico W)
led = machine.Pin("LED", machine.Pin.OUT) 

# --- Parameters ---
# Number of samples to establish the 'average' light level
BASELINE_SAMPLES = 3000 
# Sensitivity threshold (adjust this if it's too sensitive or not enough)
THRESHOLD = 75

# Minimum time between beats in ms (prevents double-counting one beat)
MIN_BEAT_MS = 300       

# --- State Variables ---
last_beat_time = 0

def get_reading(samples):
    """Calculates an average of multiple ADC readings to smooth noise."""
    total = 0
    for _ in range(samples):
        total += sensor.read_u16()
    return total / samples

print("Starting HRM-2511B Heartbeat Detector...")
print("Place finger firmly on the sensor.")
i = 0
while True:
    # 1. Get a fast snapshot (Short-term average)
    current_val = get_reading(10)
    
    #print(current_val)
    # 2. Get the background light level (Long-term baseline)
    # We do this continuously to account for finger movement/pressure changes
    baseline = get_reading(BASELINE_SAMPLES)
    
    # 3. Calculate the signal 'Pulse'
    # This removes the DC offset (constant light) and leaves the AC signal (pulse)
    pulse_signal = current_val - baseline
    
    current_time = time.ticks_ms()
    
    # 4. Check for a Beat
    if pulse_signal > THRESHOLD:
        if (current_time - last_beat_time) > MIN_BEAT_MS:
            # We have a heartbeat!
            interval = current_time - last_beat_time
            
            bpm = 60000 / interval
            
            # Flash LED and Print
            led.value(1)
            print(f"❤️ BEAT DETECTED | Signal: {pulse_signal:.0f} | Est. BPM: {bpm:.1f}")
            
            last_beat_time = current_time
            time.sleep(0.02) # Hold LED on briefly
            led.value(0)

    # Optional: Print raw signal for Thonny Plotter
    # print((pulse_signal,))
    
    time.sleep(0.0005)