#!/usr/bin/env python3
import serial
import serial.tools.list_ports
import subprocess
import time
from datetime import datetime
from typing import Optional, Any, List

class RaspberryPiController:
    def __init__(self, serial_port: Optional[str] = None, baud_rate: int = 115200):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.ser: Optional[serial.Serial] = None
        self.initialize_serial()
        
    def initialize_serial(self) -> None:
        """Initialize or reinitialize serial connection"""
        while True:
            try:
                if self.serial_port is None:
                    self.serial_port = self.detect_esp_port()
                    if self.serial_port is None:
                        print(f"{self.timestamp()} - Waiting for ESP32 device...")
                        time.sleep(2)
                        continue
                
                print(f"{self.timestamp()} - Attempting to connect to {self.serial_port} at {self.baud_rate} baud...")
                self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
                time.sleep(2)  # Wait for connection to establish
                
                # Clear any existing input buffer
                if self.ser.is_open:
                    self.ser.reset_input_buffer()
                    print(f"{self.timestamp()} - Serial connection established with {self.serial_port}")
                    print(f"{self.timestamp()} - Ready to receive commands...")
                    return
                
                print(f"{self.timestamp()} - Connection failed. Retrying...")
                self.close_serial()
                time.sleep(2)
                    
            except serial.SerialException as ser_exc:
                print(f"{self.timestamp()} - Serial error: {ser_exc}")
                print(f"{self.timestamp()} - Retrying in 2 seconds...")
                self.close_serial()
                time.sleep(2)
            except Exception as exc:
                print(f"{self.timestamp()} - Unexpected error: {exc}")
                self.close_serial()
                time.sleep(2)
    
    def close_serial(self) -> None:
        """Safely close serial connection"""
        if self.ser is not None and self.ser.is_open:
            try:
                self.ser.close()
            except Exception as exc:
                print(f"{self.timestamp()} - Error closing serial: {exc}")
        self.ser = None
    
    def detect_esp_port(self) -> Optional[str]:
        """Try to automatically detect ESP32 serial port"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'USB' in port.description or 'Serial' in port.description or 'ESP' in port.description:
                print(f"{self.timestamp()} - Found potential ESP32 at {port.device}")
                return port.device
        return None
    
    def process_commands(self) -> None:
        """Main loop to process incoming commands"""
        while True:
            try:
                if self.ser is None or not self.ser.is_open:
                    print(f"{self.timestamp()} - Serial connection not active, attempting to reconnect...")
                    self.initialize_serial()
                    continue
                
                # Read all available data from serial
                try:
                    if self.ser.in_waiting > 0:  # type: ignore[union-attr]
                        line = self.ser.readline().decode('utf-8').strip()  # type: ignore[union-attr]
                        if line:  # Only process non-empty lines
                            self.process_line(line)
                except UnicodeDecodeError:
                    print(f"{self.timestamp()} - Received malformed data")
                except serial.SerialException:
                    print(f"{self.timestamp()} - Serial error while reading, connection may be lost")
                    self.close_serial()
                except Exception as exc:
                    print(f"{self.timestamp()} - Error processing data: {exc}")
                
                # Small delay to prevent CPU overload
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\nUser interrupted. Exiting...")
                break
            except Exception as exc:
                print(f"\nUnexpected error: {exc}")
                time.sleep(1)  # Prevent tight error loop
    
    def process_line(self, line: str) -> None:
        """Process a single line of input from serial"""
        print(f"{self.timestamp()} - ESP32: {line}")
        
        try:
            if line == "TAKE_POTATO":
                self._run_python_script("take_potato.py")
                self.send_response("OK")
                
            elif line == "IS_RED_GOOD":
                result = str(self._run_python_script("is_red_good.py"))
                self.send_response(f"RESULT:{result}")
                
            elif line == "FIND_BOX_COLOR":
                result = self._run_python_script("find_box_color.py")
                self.send_response(f"RESULT:{result}")
                
            elif line.startswith("OPEN_GATE:"):
                value = float(line.split(':')[1])
                self._run_python_script("open_gate.py", str(value))
                self.send_response("OK")

            elif line == "TAKE_RIGHT_BOX":
                self._run_python_script("take_right_box.py")
                self.send_response("OK")

            elif line == "TAKE_FRONT_BOX":
                self._run_python_script("take_front_box.py")
                self.send_response("OK")

            elif line == "PLACE_RIGHT_BOX":
                self._run_python_script("play_right_box.py")
                self.send_response("OK")

            elif line == "PLACE_FRONT_BOX":
                self._run_python_script("play_front_box.py")
                self.send_response("OK")
                
            elif line == "DETECT_DRY_POT":
                result = self._run_python_script("detect_dry_pot.py")
                self.send_response(f"RESULT:{result}")
                
            elif line == "TAKE_WATER":
                self._run_python_script("take_water.py")
                self.send_response("OK")
                
            elif line == "WATER_POT":
                self._run_python_script("water_pot.py")
                self.send_response("OK")
                
            elif line == "PLAY_STARMAN":
                self._run_python_script("play_starman.py")
                self.send_response("OK")
                
            elif line:  # Only send error for non-empty lines
                self.send_response("ERROR: Unknown command")
                
        except Exception as exc:
            print(f"{self.timestamp()} - Error processing command: {exc}")
            self.send_response(f"ERROR: {str(exc)}")
    
    def send_response(self, message: str) -> None:
        """Helper method to send responses with newline"""
        if self.ser is not None and self.ser.is_open:
            try:
                self.ser.write(f"{message}\n".encode())  # type: ignore[union-attr]
            except Exception as exc:
                print(f"{self.timestamp()} - Failed to send response: {exc}")
                self.close_serial()
        else:
            print(f"{self.timestamp()} - Cannot send response, serial connection not available")
    
    def _run_python_script(self, script_name: str, *args: str) -> str:
        """Run a python script and return its output"""
        try:
            cmd: List[str] = ["python3", script_name] + list(args)
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"{self.timestamp()} - Script {script_name} failed with error:")
                print(result.stderr)
                return "false"
                
            return result.stdout.strip() or "true"
            
        except FileNotFoundError:
            print(f"{self.timestamp()} - Script not found: {script_name}")
            return "false"
        except Exception as exc:
            print(f"{self.timestamp()} - Error running {script_name}: {exc}")
            return "false"
    
    def timestamp(self) -> str:
        """Return formatted timestamp"""
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

if __name__ == '__main__':
    print("Starting Raspberry Pi Controller...")
    controller = RaspberryPiController()
    try:
        controller.process_commands()
    except Exception as exc:
        print(f"Fatal error: {exc}")
    finally:
        controller.close_serial()
        print("Program terminated")


