#!/usr/bin/env python3
import cv2
import numpy as np
import time

def detect_boxes():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "error"
    
    # Size constraints for ~25cm distance (adjust as needed)
    MIN_BOX_AREA = 10000
    MAX_BOX_AREA = 300000
    
    # HSV color ranges
    RED_LOWER1 = np.array([0, 120, 70])
    RED_UPPER1 = np.array([10, 255, 255])
    RED_LOWER2 = np.array([170, 120, 70])
    RED_UPPER2 = np.array([180, 255, 255])
    BLUE_LOWER = np.array([100, 150, 50])
    BLUE_UPPER = np.array([130, 255, 255])
    
    start_time = time.time()
    result = "null"
    
    try:
        while time.time() - start_time < 3:  # Run for 3 seconds
            ret, frame = cap.read()
            if not ret:
                continue
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Detect red
            red_mask = cv2.inRange(hsv, RED_LOWER1, RED_UPPER1) | \
                      cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)
            red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Detect blue
            blue_mask = cv2.inRange(hsv, BLUE_LOWER, BLUE_UPPER)
            blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Check red contours
            for cnt in red_contours:
                area = cv2.contourArea(cnt)
                if MIN_BOX_AREA < area < MAX_BOX_AREA:
                    result = "red"
                    break
            
            # Check blue contours if red not found
            if result != "red":
                for cnt in blue_contours:
                    area = cv2.contourArea(cnt)
                    if MIN_BOX_AREA < area < MAX_BOX_AREA:
                        result = "blue"
                        break
    
    finally:
        cap.release()
    
    return result

if __name__ == '__main__':
    print(detect_boxes())