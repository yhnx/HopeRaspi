#!/usr/bin/env python3
import cv2
import numpy as np
import sys
import time
from adafruit_servokit import ServoKit
import board
import busio
import RPi.GPIO as GPIO



def detect_ball_color():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Camera not accessible", file=sys.stderr)
        return "error"
    
    try:
        start_time = time.time()
        orange_detected = False
        
        while time.time() - start_time < 3:  # Run for 3 seconds
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Convert to HSV and create orange mask
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_orange = np.array([5, 100, 100])
            upper_orange = np.array([15, 255, 255])
            mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
            
            # Find contours
            contours, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Check for orange balls of appropriate size
            min_ball_area = 10000
            max_ball_area = 50000000
            
            for c in contours:
                area = cv2.contourArea(c)
                if min_ball_area < area < max_ball_area:
                    orange_detected = True
                    break  # Found orange, no need to check further
            
            if orange_detected:
                break  # Exit early if orange detected
        
        return "orange" if orange_detected else "white"
    
    finally:
        cap.release()

class PotatoServoController:
    def __init__(self):
        try:
            print("Initializing Potato Servo Controller...")
            
            # Initialize I2C bus
            self.i2c = busio.I2C(board.SCL, board.SDA)
            
            # Initialize ServoKit with I2C
            self.kit = ServoKit(channels=16, i2c=self.i2c)
            
            # Configure servos
            for channel in range(16):
                self.kit.servo[channel].set_pulse_width_range(500, 2400)
                self.kit.servo[channel].actuation_range = 180
            
            # Define servo channels
            self.base_servo = 13    # Base rotation
            self.shoulder_servo = 14  # Shoulder joint
            self.elbow_servo = 15    # Elbow joint
            
            # Setup GPIO for suction
            self.sucker_pin = 17
            GPIO.setup(self.sucker_pin, GPIO.OUT)
            GPIO.output(self.sucker_pin, GPIO.LOW)
            
            print("Potato Servo Controller initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize: {e}")
            raise

    def set_servo_angle(self, channel, angle):
        """Set servo to specific angle"""
        if not 0 <= channel <= 15:
            print(f"Invalid channel: {channel}")
            return False
        if not 0 <= angle <= 180:
            print(f"Invalid angle: {angle}")
            return False
            
        try:
            self.kit.servo[channel].angle = angle
            print(f"Servo {channel} set to {angle}°")
            return True
        except Exception as e:
            print(f"Error setting servo: {e}")
            return False

    def turn_servo_to_angle_with_speed(self, channel, target_angle, speed=0.5):
        """Move servo smoothly to target angle"""
        try:
            current_angle = self.kit.servo[channel].angle or 0
            step = max(1, int(3 * speed))
            
            if current_angle < target_angle:
                for angle in range(int(current_angle), int(target_angle) + 1, step):
                    self.kit.servo[channel].angle = angle
                    time.sleep(0.03 / speed)
            else:
                for angle in range(int(current_angle), int(target_angle) - 1, -step):
                    self.kit.servo[channel].angle = angle
                    time.sleep(0.03 / speed)
                    
            self.kit.servo[channel].angle = target_angle
            return True
        except Exception as e:
            print(f"Error moving servo: {e}")
            return False

    def sucker_on(self):
        """Activate suction"""
        GPIO.output(self.sucker_pin, GPIO.HIGH)
        time.sleep(0.5)

    def sucker_off(self):
        """Deactivate suction"""
        GPIO.output(self.sucker_pin, GPIO.LOW)

    def move_to_home_position(self, speed=0.6):
        """Return arm to home position"""
        self.turn_servo_to_angle_with_speed(self.elbow_servo, 180, speed)
        self.turn_servo_to_angle_with_speed(self.shoulder_servo, 100, speed)
        self.turn_servo_to_angle_with_speed(self.base_servo, 180, speed)

    def position_arm(self, base_angle, shoulder_angle, elbow_angle, speed=0.6):
        """Position all arm servos"""
        self.turn_servo_to_angle_with_speed(self.base_servo, base_angle, speed)
        self.turn_servo_to_angle_with_speed(self.shoulder_servo, shoulder_angle, speed)
        self.turn_servo_to_angle_with_speed(self.elbow_servo, elbow_angle, speed)

    def take_potato_right(self):
        """Pick up potato from right position"""
        print("\n----- TAKING POTATO FROM RIGHT -----")
        self.position_arm(base_angle=60, shoulder_angle=60, elbow_angle=13, speed=0.7)
        time.sleep(0.2)
        self.position_arm(base_angle=60, shoulder_angle=7, elbow_angle=13, speed=0.6)
        time.sleep(0.2)
        self.sucker_on()
        time.sleep(3)
        self.position_arm(base_angle=60, shoulder_angle=60, elbow_angle=13, speed=0.7)

    def place_potato_orange(self):
        """Place potato in orange container"""
        print("\n----- PLACING POTATO IN ORANGE CONTAINER -----")
        self.position_arm(base_angle=5, shoulder_angle=126, elbow_angle=0, speed=0.6)
        time.sleep(0.2)
        self.sucker_off()
        time.sleep(3)
        self.move_to_home_position()

    def place_potato_white(self):
        """Place potato in white container"""
        print("\n----- PLACING POTATO IN WHITE CONTAINER -----")
        self.position_arm(base_angle=150, shoulder_angle=85, elbow_angle=180, speed=0.6)
        time.sleep(0.2)
        self.sucker_off()
        time.sleep(3)
        self.move_to_home_position()

    def cleanup(self):
        """Clean up resources"""
        try:
            GPIO.output(self.sucker_pin, GPIO.LOW)
            print("GPIO cleaned up")
        except:
            pass

if __name__ == '__main__':
    try:
       
        
        # Detect ball color
        result = detect_ball_color()
        print(f"Detected color: {result}")
        
        controller = PotatoServoController()
        
        if result == "orange":
            
            controller.take_potato_right()
            
            time.sleep(0.5)
            controller.place_potato_orange()
        else:
            
            controller.take_potato_right()
            
            time.sleep(0.5)
            controller.place_potato_white()
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'controller' in locals():
            controller.cleanup()
        
        GPIO.cleanup()
        print("Program ended")