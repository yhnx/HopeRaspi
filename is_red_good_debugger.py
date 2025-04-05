#!/usr/bin/env python3
import cv2
import numpy as np

def show_apriltag_debug():
    # Initialize detector with optimized parameters
    params = cv2.aruco.DetectorParameters()
    params.adaptiveThreshWinSizeMin = 3
    params.adaptiveThreshWinSizeMax = 23
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_16h5)
    detector = cv2.aruco.ArucoDetector(aruco_dict, params)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Camera not accessible", file=sys.stderr)
        return

    cv2.namedWindow("AprilTag Debug View", cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("WARNING: Frame capture failed", file=sys.stderr)
                continue

            # Preprocessing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)

            # Detection
            corners, ids, _ = detector.detectMarkers(enhanced)
            debug_frame = frame.copy()

            # Visualization
            if ids is not None:
                for i, tag_id in enumerate(ids):
                    # Draw detected markers
                    color = (0, 255, 0) if tag_id % 2 == 0 else (0, 0, 255)
                    cv2.aruco.drawDetectedMarkers(debug_frame, corners, ids, borderColor=color)

                    # Label with ID and corner points
                    center = np.mean(corners[i][0], axis=0)
                    cv2.putText(debug_frame, f"ID:{tag_id[0]}", 
                               (int(center[0]), int(center[1]) - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Create processing steps visualization
            proc_vis = np.zeros((frame.shape[0], 300, 3), dtype=np.uint8)
            y_offset = 20

            # Original frame
            cv2.putText(proc_vis, "Original", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            proc_vis[y_offset+10:y_offset+130, 10:290] = cv2.resize(frame, (280, 120))

            # Enhanced view
            y_offset += 140
            cv2.putText(proc_vis, "Enhanced", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            proc_vis[y_offset+10:y_offset+130, 10:290] = cv2.resize(enhanced_bgr, (280, 120))

            # Detection info
            y_offset += 140
            status = f"Tags: {len(ids) if ids is not None else 0}"
            cv2.putText(proc_vis, status, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

            # Combine views
            combined = np.hstack((debug_frame, proc_vis))
            cv2.imshow("AprilTag Debug View", combined)

            if cv2.waitKey(30) == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    show_apriltag_debug()