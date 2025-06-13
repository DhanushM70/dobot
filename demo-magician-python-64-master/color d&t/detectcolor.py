# © 2025 Dilip Kumar S and Gokul S. All Rights Reserved.
# Authors: Dilip Kumar S , Gokul S
# Date: 2025-01-01
# This script is part of a proprietary project and may not be copied,
# modified, distributed, or used without explicit written permission 
# from the authors.
#
# This work was developed as part of a project at the Department of Robotics 
# and Automation, Rajalakshmi Engineering College, under the mentorship of 
# Mr. Ramkumar and guidance of our HoD, Dr. Giri.
#
# WARNING: Any attempt to remove or alter this notice is strictly prohibited.
import cv2
import numpy as np
import json

# Load the taught colors
with open("color d&t/taught_colors.json", "r") as f:
    taught_colors = json.load(f)

def detect_cube_position(position_type):
    """
    Detect cube colors (three at once) for either initial or final position
    Args:
        position_type: String, either "INITIAL" or "FINAL"
    Returns:
        List of detected colors
    """
    matrix = [None, None, None]
    json_filename = "color d&t/cube_matrix.json" if position_type == "INITIAL" else "color d&t/final_cube_matrix.json"

    cap = cv2.VideoCapture(0)
    print(f"{position_type} POSITION: Show all 3 cube faces to the camera. Press ENTER to confirm detection.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        output_frame = frame.copy()
        detected_regions = []

        for color_name, ranges in taught_colors.items():
            lower = np.array(ranges["lower"])
            upper = np.array(ranges["upper"])
            mask = cv2.inRange(hsv, lower, upper)
            mask = cv2.erode(mask, None, iterations=1)
            mask = cv2.dilate(mask, None, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 1000:
                    x, y, w, h = cv2.boundingRect(cnt)
                    detected_regions.append((x, color_name))
                    cv2.rectangle(output_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(output_frame, color_name, (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Sort detected regions by x (left to right)
        detected_regions = sorted(detected_regions, key=lambda tup: tup[0])
        matrix = [region[1] for region in detected_regions[:3]]  # Take up to 3 colors

        # Display detected matrix
        cv2.putText(output_frame, f"{position_type} Matrix: {matrix}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(output_frame, "Press ENTER to confirm or 'q' to quit", (10, 460), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.imshow(f"{position_type} Position - Color Detection", output_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 13:  # ENTER key
            print(f"{position_type} Matrix confirmed: {matrix}")
            break

    # Save result to JSON
    with open(json_filename, "w") as f:
        json.dump(matrix, f)

    cap.release()
    cv2.destroyAllWindows()
    return matrix


# Main execution
print("Starting cube position detection process")
print("First, we'll detect the INITIAL position of the cube")
initial_matrix = detect_cube_position("INITIAL")

print("\n-----------------------------------------------------")
print("Now, we'll detect the FINAL position of the cube")
print("Please position your cube in its final state.")
input("Press ENTER when ready to begin final position detection...")
final_matrix = detect_cube_position("FINAL")

print("\n-----------------------------------------------------")
print("Detection complete!")
print(f"Initial cube matrix: {initial_matrix}")
print(f"Final cube matrix: {final_matrix}")
print("The data has been saved to 'cube_matrix.json' and 'final_cube_matrix.json'")
