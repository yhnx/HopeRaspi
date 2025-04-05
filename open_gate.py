#!/usr/bin/env python3
import time
import sys
from adafruit_servokit import ServoKit
import board
import busio

class GateController:
    def __init__(self):
        # Initialize I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Initialize the ServoKit
        self.kit = ServoKit(channels=16)
        
        # Configure servo parameters for channels 9 and 10
        for channel in [5, 6]:
            self.kit.servo[channel].set_pulse_width_range(500, 2400)
            self.kit.servo[channel].actuation_range = 180
        
        # Set initial positions (closed)
        self.kit.servo[5].angle = 0    # Orange gate closed
        self.kit.servo[6].angle = 0   # White gate closed
        time.sleep(0.5)
        
        print("Gate Controller initialized")

    def open_gate(self, gate_type):
        """
        Open the specified gate (1 for orange, 0 for white)
        
        Args:
            gate_type (int): 1 for orange, 0 for white
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if gate_type == 1:  # Orange
                self.kit.servo[5].angle = 90   # Open orange gate
                self.kit.servo[6].angle = 0    # Ensure white gate is closed
                print("Orange gate opened")
            elif gate_type == 0:  # White
                self.kit.servo[6].angle = 90   # Open white gate
                self.kit.servo[5].angle = 0      # Ensure orange gate is closed
                print("White gate opened")
            else:
                print(f"Error: Invalid gate type {gate_type}")
                return False
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"Error operating gate: {e}")
            return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: open_gate.py <gate_type> (1 for orange, 0 for white)")
        sys.exit(1)
    
    try:
        gate_type = int(sys.argv[1])
        if gate_type not in [0, 1]:
            raise ValueError
        
        controller = GateController()
        success = controller.open_gate(gate_type)
        
        if not success:
            sys.exit(1)
            
    except ValueError:
        print("Error: Argument must be 1 (orange) or 0 (white)")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)