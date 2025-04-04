#!/usr/bin/env python3
import cv2
import sys
import time
import numpy as np

def is_red_good(max_attempts=5, delay_sec=0.5):
    """Robust AprilTag 16h5 detector with:
    - Adaptive lighting handling
    - Perspective/size tolerance
    - Multiple validation checks"""
    
    # Enhanced detector parameters
    params = cv2.aruco.DetectorParameters()
    params.adaptiveThreshWinSizeMin = 3
    params.adaptiveThreshWinSizeMax = 23
    params.adaptiveThreshWinSizeStep = 10
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    params.cornerRefinementWinSize = 5
    params.cornerRefinementMaxIterations = 30
    params.polygonalApproxAccuracyRate = 0.05  # More tolerant to distortion
    
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_16h5)
    detector = cv2.aruco.ArucoDetector(aruco_dict, params)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Camera not accessible", file=sys.stderr)
        return "false"
    
    try:
        # Warm-up camera
        for _ in range(2):
            cap.read()
        
        for attempt in range(1, max_attempts + 1):
            # Capture multiple frames for motion robustness
            frames = []
            for _ in range(3):
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
                time.sleep(0.1)
            
            if not frames:
                print(f"Attempt {attempt}: No valid frames", file=sys.stderr)
                time.sleep(delay_sec)
                continue
            
            # Use median frame to reduce noise
            median_frame = np.median(frames, axis=0).astype(np.uint8)
            
            # Preprocessing pipeline
            gray = cv2.cvtColor(median_frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Adaptive histogram equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Detect markers with enhanced parameters
            corners, ids, _ = detector.detectMarkers(enhanced)
            
            # Validation checks
            valid_tags = []
            if ids is not None:
                for i, tag_id in enumerate(ids):
                    # Check marker shape regularity
                    peri = cv2.arcLength(corners[i][0], True)
                    approx = cv2.approxPolyDP(corners[i][0], 0.04 * peri, True)
                    
                    if len(approx) == 4:  # Only accept quadrilateral markers
                        valid_tags.append(tag_id[0])
            
            if valid_tags:
                tag_id = valid_tags[0]
                print(f"Attempt {attempt}: Valid AprilTag ID = {tag_id}", file=sys.stderr)
                
                # Debug visualization (remove in production)
                debug_frame = median_frame.copy()
                cv2.aruco.drawDetectedMarkers(debug_frame, corners, ids)
                cv2.imwrite(f"debug_{attempt}.jpg", debug_frame)
                
                return "true" if tag_id % 2 == 0 else "false"
            
            print(f"Attempt {attempt}: No valid tags detected", file=sys.stderr)
            time.sleep(delay_sec)
        
        print("WARNING: No valid detection after retries", file=sys.stderr)
        return "false"
    
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    result = is_red_good()
    print(result)