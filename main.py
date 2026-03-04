import subprocess
import sys
from time import sleep

import calibration.calibration as calibration
import robot.robot as robot
import perception.object_detection as object_detection


# ============================================================
# Utility Functions
# ============================================================

def run_streamlit():
    """Launch Streamlit UI."""
    subprocess.run(["streamlit", "run", "ui/dashboard.py"])


def calibrate_robot():
    """Run full calibration process."""
    print("Starting calibration...")
    
    calibration.capture_image()
    calibration.collect_image_points()
    robot.Get_Robot_Calibration_Points()

    print("Generating homography matrix...")
    sleep(1)

    calibration.generate_homography()
    print("Calibration completed successfully.")


def image_object_detection():
    """Capture image and detect objects."""
    print("Capturing image and detecting objects...")
    
    calibration.capture_image()
    object_detection.save_objects_with_robot_coordinates()
    object_detection.mark_coordinates_on_annotated_image()

    print("Object detection completed.")

def pick_place_color_shape():

    shape = "all"
    color = "all"

    print ("Starting pick and place operation based on color and shape...")
    print("Select object shape to pick and place:")
    print("1. Circle")
    print("2. Square")
    print("3. Triangle")
    print("4. All shapes")
    shape_choice = input("Enter shape choice (1-4): ")
    

    if shape_choice == '1':
        shape = "circle"
    elif shape_choice == '2':
        shape = "square"
    elif shape_choice == '3':
        shape = "triangle"
    elif shape_choice == '4':
        shape = "all"
    else:
        print("Invalid shape choice. Defaulting to all shapes.")
        shape = "all"


    print("\nSelect object color to pick and place:")
    print("1. Red")
    print("2. Green")
    print("3. Blue")
    print("4. Yellow")
    print("5. All colors")
    color_choice = input("Enter color choice (1-5): ")

    if color_choice == '1':
        color = "red"
    elif color_choice == '2':
        color = "green"
    elif color_choice == '3':
        color = "blue"
    elif color_choice == '4':
        color = "yellow"
    elif color_choice == '5':
        color = "all"
    else:
        print("Invalid color choice. Defaulting to all colors.")
        color = "all"
    print(f"\nRunning pick and place for shape: {shape}, color: {color}...")    
    robot.Object_Pick_and_Place(color, shape)

    print("Pick and place operation completed.")
# ============================================================
# Menu System
# ============================================================

def print_menu():
    print("\n" + "=" * 82)
    print("           Machine Vision Project - Dobot MG400")
    print("=" * 82)
    print("1. Connect to Robot                  5. Object Pick and Place")
    print("2. Disconnect from Robot             6. Pick Place with color and shape")
    print("3. Calibration                       7. Run Streamlit UI")
    print("4. Object Detection                  8. Exit ")
    print("=" * 82)


def handle_choice(choice):
    if choice == '1':
        robot.Connect_Robot()

    elif choice == '2':
        robot.Disconnect_Robot()

    elif choice == '3':
        calibrate_robot()

    elif choice == '4':
        image_object_detection()

    elif choice == '5':
        robot.Object_Pick_and_Place()

    elif choice == '6':
        pick_place_color_shape()

    elif choice == '7':
        run_streamlit()

    elif choice == '8':
        print("Exiting program. Goodbye!")
        sys.exit()
    
    # elif choice == '9':
        # robot.Load_Calibration_Data()

    else:
        print("Invalid option. Please select 1-8.")


# ============================================================
# Main Loop
# ============================================================

def main():
    while True:
        try:
            print_menu()
            choice = input("Please select an option (1-8): ")
            handle_choice(choice)

        except KeyboardInterrupt:
            print("\nProgram stopped by user.")
            sys.exit()


if __name__ == "__main__":
    main()
    
