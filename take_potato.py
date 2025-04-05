#!/usr/bin/env python3
import cv2
import numpy as np
import sys
import time

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
        # Initialize I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Initialize the ServoKit with 16 channels (the PCA9685 has 16 channels)
        self.kit = ServoKit(channels=16)
        
        # Configure default servo parameters for all channels
        for channel in range(16):
            # Set pulse width range (in microseconds)
            self.kit.servo[channel].set_pulse_width_range(500, 2400)
            
            # Set actuation range (min and max angle in degrees)
            self.kit.servo[channel].actuation_range = 180
        
        # Define servo channels for the three-link arm
        self.base_servo = 13    # Base rotation servo (horizontal rotation)
        self.shoulder_servo = 14  # Shoulder servo (first link)
        self.elbow_servo = 15     # Elbow servo (second link)
        
        # Set up GPIO for suction control
        GPIO.setmode(GPIO.BCM)
        self.sucker_pin = 17    # Using GPIO pin 17 for sucker control
        GPIO.setup(self.sucker_pin, GPIO.OUT)
        GPIO.output(self.sucker_pin, GPIO.LOW)  # Ensure sucker is off at start
        
        print("Potato Servo Controller initialized with three-link arm")

    def set_servo_angle(self, channel, angle):
        """
        Turn a specific servo to the specified angle
        
        Args:
            channel (int): The servo channel number (0-15)
            angle (float): The target angle in degrees (0-180)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Validate input parameters
        if not isinstance(channel, int) or not 0 <= channel <= 15:
            print(f"Error: Channel must be an integer between 0-15, got {channel}")
            return False
            
        if not 0 <= angle <= 180:
            print(f"Error: Angle must be between 0-180 degrees, got {angle}")
            return False
        
        try:
            # Set the servo to the specified angle
            self.kit.servo[channel].angle = angle
            print(f"Servo on channel {channel} set to {angle} degrees")
            return True
        except Exception as e:
            print(f"Error setting servo: {e}")
            return False

    def turn_servo_to_angle_with_speed(self, channel, target_angle, speed=1.0):
        """
        Turn a servo to a target angle at a controlled speed
        
        Args:
            channel (int): The servo channel number (0-15)
            target_angle (float): The target angle in degrees (0-180)
            speed (float): The movement speed (1.0 = full speed, 0.1 = very slow)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Validate input parameters
        if not 0 <= channel <= 15:
            print(f"Error: Channel must be between 0-15, got {channel}")
            return False
            
        if not 0 <= target_angle <= 180:
            print(f"Error: Target angle must be between 0-180 degrees, got {target_angle}")
            return False
            
        if not 0.1 <= speed <= 1.0:
            print(f"Error: Speed must be between 0.1-1.0, got {speed}")
            speed = max(0.1, min(speed, 1.0))  # Clamp to valid range
        
        try:
            # Get current position
            current_angle = self.kit.servo[channel].angle
            
            # If current_angle is None (servo hasn't been set yet), default to 0
            if current_angle is None:
                current_angle = 0
            
            # Calculate step size based on speed (smaller step = slower movement)
            step = max(1, 1 * speed)
            
            # Determine direction
            if current_angle < target_angle:
                # Moving forward
                for angle in range(int(current_angle), int(target_angle) + 1, int(step)):
                    self.kit.servo[channel].angle = angle
                    time.sleep(0.01 / speed)  # Adjust delay based on speed
            else:
                # Moving backward
                for angle in range(int(current_angle), int(target_angle) - 1, -int(step)):
                    self.kit.servo[channel].angle = angle
                    time.sleep(0.01 / speed)  # Adjust delay based on speed
            
            # Ensure we reach exactly the target angle
            self.kit.servo[channel].angle = target_angle
            print(f"Servo on channel {channel} moved to {target_angle} degrees")
            return True
            
        except Exception as e:
            print(f"Error controlling servo: {e}")
            return False
    def sucker_on(self):
        """Turn on the suction for grabbing potatoes"""
        print("Turning sucker ON")
        GPIO.output(self.sucker_pin, GPIO.HIGH)
        time.sleep(0.5)  # Short delay to ensure suction is established
    
    def sucker_off(self):
        """Turn off the suction to release potatoes"""
        print("Turning sucker OFF")
        GPIO.output(self.sucker_pin, GPIO.LOW)
    
    def move_to_home_position(self, speed=0.3):
        """Move the arm to the home/resting position"""
        print("Moving to home position...")
        # Move arm segments first, then base to avoid collisions
        self.turn_servo_to_angle_with_speed(self.elbow_servo, 180, speed)
        time.sleep(0.3)
        self.turn_servo_to_angle_with_speed(self.shoulder_servo, 120, speed)
        time.sleep(0.3)
        return self.turn_servo_to_angle_with_speed(self.base_servo, 20, speed)
    
    def position_arm(self, base_angle, shoulder_angle, elbow_angle, speed=0.3):
        """
        Position all three arm segments at specified angles
        
        Args:
            base_angle (float): Angle for base servo (0-180)
            shoulder_angle (float): Angle for shoulder servo (0-180)
            elbow_angle (float): Angle for elbow servo (0-180)
            speed (float): Movement speed (0.1-1.0)
        """
        print(f"Positioning arm: base={base_angle}, shoulder={shoulder_angle}, elbow={elbow_angle}")
        
        # Move base first
        self.turn_servo_to_angle_with_speed(self.base_servo, base_angle, speed)
        time.sleep(0.2)
        
        # Move shoulder and elbow together for smoother motion
        self.turn_servo_to_angle_with_speed(self.elbow_servo, elbow_angle, speed)
        time.sleep(0.5)
        self.turn_servo_to_angle_with_speed(self.shoulder_servo, shoulder_angle, speed)
        time.sleep(0.5)
    
    def take_potato_front(self):
        """Sequence to take a potato from the front position"""
        print("\n----- TAKING POTATO FROM FRONT -----")
        
        # Position arm over potato
        self.position_arm(base_angle=20, shoulder_angle=30, elbow_angle=30, speed=0.4)
        time.sleep(0.5)
        
        # Lower arm to potato position
        self.position_arm(base_angle=20, shoulder_angle=0, elbow_angle=0, speed=0.3)
        time.sleep(0.5)
        
        # Turn on sucker to grab potato
        self.sucker_on()
        time.sleep(1)  # Wait for suction to properly grab potato
        
        # Lift arm with potato
        self.position_arm(base_angle=20, shoulder_angle=70, elbow_angle=90, speed=0.3)
        
        print("Potato successfully taken from front position")

        
    def take_potato_right(self):
        """Sequence to take a potato from the right position"""
        print("\n----- TAKING POTATO FROM RIGHT -----")
        
        # Position arm over right potato
        self.position_arm(base_angle=110, shoulder_angle=30, elbow_angle=30, speed=0.4)
        time.sleep(0.5)
        
        # Lower arm to potato position
        self.position_arm(base_angle=110, shoulder_angle=0, elbow_angle=0, speed=0.3)
        time.sleep(0.5)
        
        # Turn on sucker to grab potato
        self.sucker_on()
        time.sleep(1)  # Wait for suction to properly grab potato
        
        # Lift arm with potato
        self.position_arm(base_angle=110, shoulder_angle=70, elbow_angle=90, speed=0.3)
        
        print("Potato successfully taken from right position")
        
    def take_potato_left(self):
        """Sequence to take a potato from the left position"""
        print("\n----- TAKING POTATO FROM LEFT -----")
        
        # Position arm over left potato
        self.position_arm(base_angle=110, shoulder_angle=150, elbow_angle=150, speed=0.4)
        time.sleep(0.5)
        
        # Lower arm to potato position
        self.position_arm(base_angle=110, shoulder_angle=180, elbow_angle=180, speed=0.3)
        time.sleep(0.5)
        
        # Turn on sucker to grab potato
        self.sucker_on()
        time.sleep(1)  # Wait for suction to properly grab potato
        
        # Lift arm with potato
        self.position_arm(base_angle=110, shoulder_angle=110, elbow_angle=90, speed=0.3)
        
        print("Potato successfully taken from left position")
        
    def place_potato_orange(self):
        """Sequence to place a potato in the orange container"""
        print("\n----- PLACING POTATO IN orange CONTAINER -----")
        
        # Position arm over orange container
        self.position_arm(base_angle=0, shoulder_angle=80, elbow_angle=90, speed=0.4)
        time.sleep(0.5)
        
        # Lower arm to place potato
        self.position_arm(base_angle=0, shoulder_angle=90, elbow_angle=180, speed=0.3)
        time.sleep(0.5)
        
        # Turn off sucker to release potato
        self.sucker_off()
        time.sleep(3)  # Wait 3 seconds for potato to fully release
        
        # Lift arm after releasing
        # self.position_arm(base_angle=180, shoulder_angle=60, elbow_angle=90, speed=0.3)
        
        # Return to home position
        self.move_to_home_position()
        
        print("Potato successfully placed in orange container")
    def place_potato_white(self):
        """Sequence to place a potato in the right container"""
        print("\n----- PLACING POTATO IN RIGHT CONTAINER -----")
        
        # Position arm over right container
        self.position_arm(base_angle=40, shoulder_angle=80, elbow_angle=90, speed=0.4)
        time.sleep(0.5)
        
        # Lower arm to place potato
        self.position_arm(base_angle=40, shoulder_angle=90, elbow_angle=180, speed=0.3)
        time.sleep(0.5)
        
        # Turn off sucker to release potato
        self.sucker_off()
        time.sleep(3)  # Wait 3 seconds for potato to fully release
        
        # Lift arm after releasing
        # self.position_arm(base_angle=0, shoulder_angle=60, elbow_angle=90, speed=0.3)
        
        # Return to home position
        self.move_to_home_position()
        
        print("Potato successfully placed in right container")
    
    def cleanup(self):
        """Clean up GPIO pins on program exit"""
        print("Cleaning up GPIO...")
        try:
            # Check if GPIO is already in a mode
            current_mode = GPIO.getmode()
        
            # If not, we need to set it again
            if current_mode is None:
                GPIO.setmode(GPIO.BCM)
            
            GPIO.output(self.sucker_pin, GPIO.LOW)  # Ensure sucker is off
        except Exception as e:
            print(f"Warning during cleanup: {e}")
        finally:
            # Always try to clean up GPIO
            try:
                GPIO.cleanup()
            except:
                pass
        
    def demo(self):
        """Demo function to test the potato handling sequences"""
        print("Running potato handling demonstration...")
        
        try:
            # Start from home position
            self.move_to_home_position()
            time.sleep(1)
            
            # Demo each sequence
            self.take_potato_front()
            time.sleep(1)
            self.place_potato_orange()
            time.sleep(1)
            
            self.take_potato_right()
            time.sleep(1)
            self.place_potato_white()
            time.sleep(1)
            
            self.take_potato_left()
            time.sleep(1)
            self.place_potato_orange()
            
            print("\nDemonstration complete")
            
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
        finally:
            # Always clean up GPIO on exit
            self.cleanup()


if __name__ == '__main__':
    result = detect_ball_color()
    print(result)
    
    try:
        # Create controller instance
        controller = PotatoServoController()
        
        # Run the demo to test all functions
        #controller.demo()

        if result == "orange":
            controller.take_potato_right()
            time.sleep(1)
            controller.place_potato_orange()
        else:
            controller.take_potato_right()
            time.sleep(1)
            controller.place_potato_white()
        
        # Alternatively, you can uncomment to run individual commands:
        # controller.take_potato_front()
        # time.sleep(1)
        # controller.place_potato_orange()
        
    except Exception as e:
        print(f"Error running program: {e}")
    finally:
        # Clean up GPIO if controller was initialized
        if 'controller' in locals():
            controller.cleanup()
        
    print("\nExiting program")


    
    
