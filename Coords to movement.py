import machine
import time
import math



# -- Observer's Location (Hyderabad, India) --

LATITUDE = 17.4065
LONGITUDE = 78.4772

# -- Stepper Motor GPIO Pins on ESP32 --

RA_STEP_PIN = machine.Pin(12, machine.Pin.OUT) # Azimuth motor
RA_DIR_PIN = machine.Pin(14, machine.Pin.OUT) 

DEC_STEP_PIN = machine.Pin(27, machine.Pin.OUT) # Altitude motor
DEC_DIR_PIN = machine.Pin(26, machine.Pin.OUT) 

# -- Mechanical Properties --
# Example: (200 steps/rev * 16 microsteps) / (360 degrees / 50 gear ratio) = 444.44
STEPS_PER_DEGREE_RA = 444.44
STEPS_PER_DEGREE_DEC = 444.44

# -- Telescope's Current Position (Global Variables) --

current_altitude = 90.0
current_azimuth = 0.0

# --- 2. HELPER FUNCTIONS ---

def setup_rtc():
    
    rtc = machine.RTC()
    
    rtc.datetime((2025, 7, 22, 2, 12, 0, 0, 0)) #enter the time
    print("RTC synchronized:", rtc.datetime())

def move_stepper(step_pin, dir_pin, steps, step_delay_us=500):
    
    if steps == 0:
        return
        
    direction = 1 if steps > 0 else 0
    dir_pin.value(direction)
    
    for _ in range(abs(steps)):
        step_pin.value(1)
        time.sleep_us(step_delay_us)
        step_pin.value(0)
        time.sleep_us(step_delay_us)

def ra_dec_to_alt_az(ra, dec, lat, lon):
    
    # Get current UTC time from RTC
    now_utc = time.gmtime()
    year, month, day, hour, minute, second, _, _ = now_utc

    # Calculate Julian Date for J2000.0
    jd = 367 * year - 7 * (year + (month + 9) // 12) // 4 + 275 * month // 9 + day - 730530
    jd += (hour + minute / 60 + second / 3600) / 24.0

    # Calculate Local Sidereal Time (LST)
    lst = 100.46 + 0.985647 * jd + lon + 15 * (hour + minute / 60 + second / 3600)
    lst = lst % 360 # Keep it within 0-360 degrees

    # Calculate Hour Angle (HA)
    ha = lst - ra
    if ha < 0:
        ha += 360
        
    # Convert all to radians for math functions
    ra_rad = math.radians(ra)
    dec_rad = math.radians(dec)
    ha_rad = math.radians(ha)
    lat_rad = math.radians(lat)

    # Altitude calculation
    sin_alt = math.sin(dec_rad) * math.sin(lat_rad) + math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha_rad)
    alt = math.asin(sin_alt)

    # Azimuth calculation
    cos_az = (math.sin(dec_rad) - math.sin(alt) * math.sin(lat_rad)) / (math.cos(alt) * math.cos(lat_rad))
    az = math.acos(cos_az)

    # Convert results back to degrees
    alt_deg = math.degrees(alt)
    az_deg = math.degrees(az)
    
    # Adjust azimuth based on hour angle
    if math.sin(ha_rad) > 0:
        az_deg = 360 - az_deg

    return alt_deg, az_deg

# --- 3. MAIN LOGIC ---

def goto_coordinates(ra_target, dec_target):
    
    global current_altitude, current_azimuth
    
    print(f"Current position: Alt={current_altitude:.2f}°, Az={current_azimuth:.2f}°")
    
    # 1. Calculate where the target is right now
    target_alt, target_az = ra_dec_to_alt_az(ra_target, dec_target, LATITUDE, LONGITUDE)
    print(f"Target is at: Alt={target_alt:.2f}°, Az={target_az:.2f}°")
    
    # 2. Calculate the difference in angles
    delta_alt = target_alt - current_altitude
    delta_az = target_az - current_azimuth
    
    # Handle azimuth wraparound (e.g., moving from 350° to 10°)
    if delta_az > 180:
        delta_az -= 360
    elif delta_az < -180:
        delta_az += 360
        
    print(f"Movement required: ΔAlt={delta_alt:.2f}°, ΔAz={delta_az:.2f}°")

    # 3. Convert angle difference to stepper motor steps
    dec_steps = int(delta_alt * STEPS_PER_DEGREE_DEC)
    ra_steps = int(delta_az * STEPS_PER_DEGREE_RA)
    
    print(f"Moving DEC motor by {dec_steps} steps.")
    print(f"Moving RA motor by {ra_steps} steps.")
    
    # 4. Move the motors (can be done sequentially or simultaneously with threading)
    move_stepper(DEC_STEP_PIN, DEC_DIR_PIN, dec_steps)
    move_stepper(RA_STEP_PIN, RA_DIR_PIN, ra_steps)
    
    # 5. Update the telescope's current position
    current_altitude = target_alt
    current_azimuth = target_az
    
    print("Movement complete. New position: Alt={current_altitude:.2f}°, Az={current_azimuth:.2f}°")

# --- 4. EXECUTION ---

if __name__ == "__main__":
    # Initialize the RTC (run this once with the correct time)
    setup_rtc()
    
    # Example Target: Polaris (The North Star)
    
    polaris_ra = 37.95
    polaris_dec = 89.26
    
    
    goto_coordinates(polaris_ra, polaris_dec)
