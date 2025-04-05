import RPi.GPIO as GPIO
import time

BUZZER_PIN = 15  # BCM pin 15

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Define rhythm pattern (on duration, off duration)
# Based on the chorus: "There's a starman waiting in the sky..."
pattern = [
    (0.3, 0.1),  # There's
    (1.4, 0.2),  # a
    (1.4, 0.2),   # star-
    (0.3, 0.1),  # man
    
    (0.3, 0.1),
    (0.3, 0.1),
    (0.3, 0.1),
    
    (1.4, 0.2),   # star-

    
]

def play_buzz_rhythm():
    print("?? Buzzer playing: Starman Chorus")
    for on_time, off_time in pattern:
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(on_time)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(off_time)

try:
    play_buzz_rhythm()
finally:
    GPIO.cleanup()
    print("All done folks! ??")

