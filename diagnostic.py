import machine
import time

# --- Setup ---
sensor = machine.ADC(27)
led = machine.Pin("LED", machine.Pin.OUT) 

MIN_BEAT_MS = 300       
last_beat_time = 0

print("Starting Diagnostic Mode...")
print("PLACE YOUR FINGER ON THE SENSOR NOW.")

# --- Calibration Phase ---
# Give you 3 seconds to place your finger and hold it steady
for i in range(3, 0, -1):
    print(f"Calibrating baseline in {i}...")
    time.sleep(1)

# Now that your finger is on the sensor, take a solid baseline reading
print("Reading baseline...")
baseline = sum(sensor.read_u16() for _ in range(50)) / 50
max_pulse = 0

print("Calibration complete! Open 'View -> Plotter' in Thonny.")

while True:
    current_val = sum(sensor.read_u16() for _ in range(10)) / 10
    baseline = (baseline * 0.99) + (current_val * 0.01)
    
    pulse_signal = current_val - baseline
    
    if pulse_signal > max_pulse:
        max_pulse = pulse_signal
    else:
        max_pulse *= 0.995  
    
    dynamic_threshold = max(max_pulse * 0.6, 5)
    
    current_time = time.ticks_ms()
    
    # Print the raw data for the Plotter
    print((pulse_signal, dynamic_threshold))

    if pulse_signal > dynamic_threshold:
        if (current_time - last_beat_time) > MIN_BEAT_MS:
            interval = current_time - last_beat_time
            bpm = 60000 / interval
            
            if 40 <= bpm <= 220:
                led.value(1)
                print("❤️")
                last_beat_time = current_time
                time.sleep(0.02)
                led.value(0)

    time.sleep(0.01)