# © 2025 Dilip Kumar S and Gokul S. All Rights Reserved.
# Authors: Dilip Kumar S , Gokul S
# Date: 2025-01-01
# This script is part of a proprietary project and may not be copied,
# modified, distributed, or used without explicit written permission 
# from the authors.
# This work was developed as part of a project at the Department of Robotics 
# and Automation, Rajalakshmi Engineering College, under the mentorship of 
# Mr. Ramkumar and guidance of our HoD, Dr. Giri.
#
# WARNING: Any attempt to remove or alter this notice is strictly prohibited.
import subprocess
import sys
import time

def run_continuous_script(script_name):
    try:
       
            subprocess.run([sys.executable, script_name])
    except KeyboardInterrupt:
        print("\nStopped continuous script.")

def main():
    user_input = input("Press 2 forv Running color teaching:"
    "\nPress 3 for Running color detection and process the goal stack process: "
    "\nPress 4 for Running cube detection for the position: "
    "\nPress 5 for Running homography matrix: "
    "\nPress q to quit: ")
    if user_input == '2':
        subprocess.run([sys.executable, "color d&t/python teach_color.py.py"])
        print("Running color teaching...")
    elif user_input == '3':
        while True:
            subprocess.run([sys.executable, "color d&t/detectcolor.py"])
            print("Running color detection...")
            run_continuous_script("Dobotcontrol.py")
 
    elif user_input == '4':
        while True:
            subprocess.run([sys.executable, "inverse/cube_detection_dobot.py"])
            print("Running cube detection for the position...")
            run_continuous_script("HELLO.py")
            time.sleep(3)
    elif user_input == '5':
        subprocess.run([sys.executable, "inverse/cam_to_dobot_matrix.npy"])
        print("Running homography matrix...")
    elif user_input.lower() == 'q':
        
        print("Exiting the program.")
        
    else:
        print("press the valid input.")

if __name__ == "__main__":
    main()
