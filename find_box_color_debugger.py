#!/usr/bin/env python3
import cv2
import numpy as np
import sys

def detect_boxes():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Camera not accessible", file=sys.stderr)
        return "error"
    
    cv2.namedWindow("Box Detector", cv2.WINDOW_NORMAL)
    
    # Size constraints (adjust for your 25cm distance)
    MIN_BOX_AREA = 10000
    MAX_BOX_AREA = 30000
    
    # Color ranges (HSV)
    RED_LOWER1 = np.array([0, 120, 70])
    RED_UPPER1 = np.array([10, 255, 255])
    RED_LOWER2 = np.array([170, 120, 70])
    RED_UPPER2 = np.array([180, 255, 255])
    BLUE_LOWER = np.array([100, 150, 50])
    BLUE_UPPER = np.array([130, 255, 255])
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to capture frame", file=sys.stderr)
                return "error"
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            display = frame.copy()
            result = "none"  # Default result
            
            # Create masks for both colors
            red_mask1 = cv2.inRange(hsv, RED_LOWER1, RED_UPPER1)
            red_mask2 = cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)
            blue_mask = cv2.inRange(hsv, BLUE_LOWER, BLUE_UPPER)
            
            # Find contours
            red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process red boxes
            for cnt in red_contours:
                area = cv2.contourArea(cnt)
                if MIN_BOX_AREA < area < MAX_BOX_AREA:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(display, (x, y), (x+w, y+h), (0, 0, 255), 3)
                    cv2.putText(display, "RED BOX", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    result = "red"
            
            # Process blue boxes
            for cnt in blue_contours:
                area = cv2.contourArea(cnt)
                if MIN_BOX_AREA < area < MAX_BOX_AREA:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(display, (x, y), (x+w, y+h), (255, 0, 0), 3)
                    cv2.putText(display, "BLUE BOX", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                    result = "blue"
            
            # Show default message if no boxes detected
            if result == "none":
                h, w = frame.shape[:2]
                cv2.putText(display, "NO BOX DETECTED", (w//2-150, h//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            
            # Create combined mask preview
            mask_display = np.zeros_like(frame)
            mask_display[red_mask > 0] = (0, 0, 255)  # Red
            mask_display[blue_mask > 0] = (255, 0, 0)  # Blue
            mask_display = cv2.resize(mask_display, (200, 150))
            
            # Add mask preview to main display
            display[0:150, 0:200] = mask_display
            cv2.putText(display, "Color Mask", (10, 170), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display status
            status = f"Status: {result.upper()}" if result != "none" else "Status: SEARCHING"
            cv2.putText(display, status, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Box Detector", display)
            
            key = cv2.waitKey(30)
            if key == ord('q'):
                return "none"
            elif key == ord('c') and result != "none":
                cv2.destroyAllWindows()
                return result
    
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    result = detect_boxes()
    print(result)


