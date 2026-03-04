import subprocess
import sys
from time import sleep

from . import calibration
from . import robot
from .perception import object_detection


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


# ============================================================
# Menu System
# ============================================================

def print_menu():
    print("\n" + "=" * 82)
    print("           Machine Vision Project - Dobot MG400")
    print("=" * 82)
    print("1. Connect to Robot")
    print("2. Disconnect from Robot")
    print("3. Calibration")
    print("4. Object Detection")
    print("5. Object Pick and Place")
    print("6. Run Streamlit UI")
    print("7. Exit")
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
        run_streamlit()

    elif choice == '7':
        print("Exiting program. Goodbye!")
        sys.exit()

    else:
        print("Invalid option. Please select 1-7.")


# ============================================================
# Main Loop
# ============================================================

def main():
    while True:
        try:
            print_menu()
            choice = input("Please select an option (1-7): ")
            handle_choice(choice)

        except KeyboardInterrupt:
            print("\nProgram stopped by user.")
            sys.exit()


if __name__ == "__main__":
    main()