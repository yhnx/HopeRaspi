#!/usr/bin/env python3
import cv2
import numpy as np
import sys

def detect_ball_color():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Camera not accessible", file=sys.stderr)
        return "error"
    
    cv2.namedWindow("Ping Pong Ball Detector", cv2.WINDOW_NORMAL)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to capture frame", file=sys.stderr)
                return "error"
            
            # Convert to HSV and create orange mask
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_orange = np.array([5, 80, 80])
            upper_orange = np.array([15, 255, 255])
            mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
            
            # Find orange balls
            contours, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            min_ball_area = 10000
            max_ball_area = 50000000
            
            display = frame.copy()
            result = "white"  # Default to white if no orange detected
            
            # Process the largest orange contour
            largest_orange = None
            max_area = 0
            for c in contours:
                area = cv2.contourArea(c)
                if min_ball_area < area < max_ball_area and area > max_area:
                    largest_orange = c
                    max_area = area
            
            if largest_orange is not None:
                # Draw orange detection
                cv2.drawContours(display, [largest_orange], -1, (0, 165, 255), 3)
                x, y, w, h = cv2.boundingRect(largest_orange)
                cv2.putText(display, "ORANGE", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 165, 255), 2)
                result = "orange"
            else:
                # Show "WHITE" in center of screen when no orange detected
                h, w = frame.shape[:2]
                cv2.putText(display, "WHITE (default)", (w//2-100, h//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            
            # Show color mask preview
            mask_display = np.zeros_like(frame)
            mask_display[mask_orange > 0] = (0, 165, 255)
            mask_display = cv2.resize(mask_display, (200, 150))
            display[0:150, 0:200] = mask_display
            cv2.putText(display, "Orange Mask", (10, 170), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display status text
            status = f"Status: {result.upper()}"
            cv2.putText(display, status, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Ping Pong Ball Detector", display)
            
            key = cv2.waitKey(30)
            if key == ord('q'):
                return "none"
            elif key == ord('c'):
                cv2.destroyAllWindows()
                return result
    
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    result = detect_ball_color()
    print(result)