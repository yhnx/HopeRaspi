# RoboHope - HopeRaspi

## Overview
RoboHope is an autonomous robot designed for the SLRC (Sri Lanka Robotics Competition) games. This repository, "HopeRaspi," contains the Raspberry Pi-based codebase for the robot's vision tasks and servo control. The project focuses on enabling the robot to complete assigned tasks through:
- **Vision Tasks**: Ball detection, color detection, and AprilTag 16h5 detection using OpenCV.
- **Servo Control**: Managing precise movements via Raspberry Pi.

The code is in active development, with various components at different stages of completion.

## Last Updated
Friday, May 30, 2025, 09:42 PM +0530

## Installation

### Prerequisites
- **Hardware**: Raspberry Pi (recommended model 4B or compatible).
- **Software**:
  - Python 3.x
  - OpenCV (for vision tasks)
  - Raspberry Pi OS or compatible Linux distribution
  - Git (for cloning the repository)

### Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/yhnx/HopeRaspi.git
   cd HopeRaspi
   ```
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   (Note: Update `requirements.txt` with necessary dependencies like `opencv-python`, `numpy`, `pyserial` if not already present.)
3. Connect the Raspberry Pi to the robot's hardware (e.g., camera for vision, servo motors, ESP32 for navigation).
4. Ensure proper permissions and GPIO access on the Raspberry Pi.

## Usage
- Run individual Python scripts based on the task:
  - **Vision Tasks**: Use `find_box_color.py` or `is_red_good.py` for color and object detection.
  - **Servo Control**: Execute `take_potato.py` for servo operations.
  - **Main Execution**: Run `raspi.py` as the primary script on the Raspberry Pi, which handles serial communication with the navigation ESP32.
- Example command to run a script:
  ```bash
  python raspi.py
  ```
- Monitor output via console or connected display. Adjust parameters in the scripts as needed based on real-time performance.

## File Descriptions
- **`README.md`**: This file.
- **`debug_1.jpg`**: Debug image.
- **`find_box_color.py`**: Script for box color detection.
- **`find_box_color_debugger.py`**: Debugging script for color detection.
- **`is_red_good.py`**: Script for red object detection.
- **`is_red_good_debugger.py`**: Debugging script for red detection.
- **`open_gate.py`**: Script for gate operation.
- **`play_starman.py`**: Script (purpose unclear).
- **`raspi.py`**: Main script for Raspberry Pi, used to run the robot's core logic with serial communication to the navigation ESP32.
- **`requirements.txt`**: Dependency file.
- **`take_potato.py`**: Script for servo control.
- **`take_potato_debugger.py`**: Debugging script for servo control.

## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request with a clear description of changes.
