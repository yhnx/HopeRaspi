#!/usr/bin/env python3
import serial
import subprocess
import time

class RaspberryPiController:
    def __init__(self, serial_port='/dev/ttyUSB0', baud_rate=115200):
        self.ser = serial.Serial(serial_port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for connection to establish
        print(f"Connected to {serial_port} at {baud_rate} baud")
        
    def process_commands(self):
        try:
            while True:
                if self.ser.in_waiting > 0:
                    command = self.ser.readline().decode('utf-8').strip()
                    print(f"Received command: {command}")
                    
                    if command == "TAKE_POTATO":
                        self._run_python_script("take_potato.py")
                        self.ser.write(b"OK\n")
                        
                    elif command == "IS_RED_GOOD":
                        result = str(self._run_python_script("is_red_good.py"))
                        self.ser.write(f"RESULT:{result}\n".encode())
                        
                    elif command == "FIND_BOX_COLOR":
                        result = self._run_python_script("find_box_color.py")
                        self.ser.write(f"RESULT:{result}\n".encode())
                        
                    elif command.startswith("OPEN_GATE:"):
                        value = float(command.split(':')[1])
                        self._run_python_script("open_gate.py", str(value))
                        self.ser.write(b"OK\n")

                    elif command == "TAKE_RIGHT_BOX":
                        self._run_python_script("take_right_box.py")
                        self.ser.write(b"OK\n")

                    elif command == "TAKE_FRONT_BOX":
                        self._run_python_script("take_front_box.py")
                        self.ser.write(b"OK\n")

                    elif command == "PLACE_RIGHT_BOX":
                        self._run_python_script("play_right_box.py")
                        self.ser.write(b"OK\n")

                    elif command == "PLACE_FRONT_BOX":
                        self._run_python_script("play_front_box.py")
                        self.ser.write(b"OK\n")
                        
                    elif command == "DETECT_DRY_POT":
                        result = self._run_python_script("detect_dry_pot.py")
                        self.ser.write(f"RESULT:{result}\n".encode())
                        
                    elif command == "TAKE_WATER":
                        self._run_python_script("take_water.py")
                        self.ser.write(b"OK\n")
                        
                    elif command == "WATER_POT":
                        self._run_python_script("water_pot.py")
                        self.ser.write(b"OK\n")
                        
                    elif command == "PLAY_STARMAN":
                        self._run_python_script("play_starman.py")
                        self.ser.write(b"OK\n")
                        
                        
                    else:
                        self.ser.write(b"ERROR: Unknown command\n")
                        
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            self.ser.close()
            
    def _run_python_script(self, script_name, *args):
        try:
            cmd = ["python3", script_name] + list(args)
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return "false"
        except Exception as e:
            print(f"Error running {script_name}: {e}")
            return "false"

if __name__ == '__main__':
    controller = RaspberryPiController()
    controller.process_commands()