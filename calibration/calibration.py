##############################################################################################
# Robot Vision Calibration System (No Class Version)
##############################################################################################

import os
import json
import cv2
import numpy as np

# --------------------------------------------------------------------------------------------
# File Paths
# --------------------------------------------------------------------------------------------
IMAGE_PATH = "./outputs/captured_img.png"
IMAGE_POINTS_PATH = "./outputs/image_calibration_points.json"
ROBOT_POINTS_PATH = "./outputs/robot_calibration_points.json"
H_MATRIX_PATH = "./outputs/H_matrix.json"


##############################################################################################
# Capture Image
##############################################################################################
def capture_image():
    print("Press SPACE to capture image")
    print("Press ESC to exit")

    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Camera", frame)
        key = cv2.waitKey(1)

        if key % 256 == 32:  # SPACE
            success = cv2.imwrite(IMAGE_PATH, frame)
            if success:
                print("Image saved successfully.")
            else:
                print("Image save FAILED.")
            break 
        elif key % 256 == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    return True


##############################################################################################
# Collect 4 Image Points
##############################################################################################
def collect_image_points():

    if not os.path.exists(IMAGE_PATH):
        print("Captured image not found.")
        return False

    image_points = []
    img = cv2.imread(IMAGE_PATH)

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(image_points) < 4:
            image_points.append([x, y])
            print(f"Point {len(image_points)}: ({x}, {y})")

            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Image", img)

            if len(image_points) == 4:
                cv2.destroyAllWindows()

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(image_points) != 4:
        print("You must select exactly 4 points.")
        return False

    save_image_points(image_points)
    return True


##############################################################################################
# Save Image Points
##############################################################################################
def save_image_points(points):

    data = {}
    for i, (x, y) in enumerate(points, start=1):
        data[f"point{i}"] = {"x": float(x), "y": float(y)}

    with open(IMAGE_POINTS_PATH, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Image points saved to {IMAGE_POINTS_PATH}")


##############################################################################################
# Generate Homography Matrix
##############################################################################################
def generate_homography():

    if not os.path.exists(ROBOT_POINTS_PATH):
        print("Robot coordinate file missing.")
        return False

    if not os.path.exists(IMAGE_POINTS_PATH):
        print("Image point file missing.")
        return False

    with open(ROBOT_POINTS_PATH, "r") as f:
        robot_data = json.load(f)

    with open(IMAGE_POINTS_PATH, "r") as f:
        image_data = json.load(f)

    robot_pts = []
    image_pts = []

    for i in range(1, 5):
        robot_pts.append([
            float(robot_data[f"point{i}"]["x"]),
            float(robot_data[f"point{i}"]["y"])
        ])
        image_pts.append([
            float(image_data[f"point{i}"]["x"]),
            float(image_data[f"point{i}"]["y"])
        ])

    robot_pts = np.array(robot_pts, dtype=np.float32)
    image_pts = np.array(image_pts, dtype=np.float32)

    # RANSAC for robustness
    H, mask = cv2.findHomography(image_pts, robot_pts, cv2.RANSAC)

    if H is None:
        print("Homography computation failed.")
        return False

    with open(H_MATRIX_PATH, "w") as f:
        json.dump(H.tolist(), f, indent=4)

    print("Homography matrix generated and saved.")
    print(H)

    return True


##############################################################################################
# Load Homography
##############################################################################################
def load_homography():

    if not os.path.exists(H_MATRIX_PATH):
        print("H matrix file not found.")
        return None

    with open(H_MATRIX_PATH, "r") as f:
        H = np.array(json.load(f))

    return H


##############################################################################################
# Convert Pixel → Robot Coordinate
##############################################################################################
def pixel_to_robot(x, y, H):

    point = np.array([[[x, y]]], dtype=np.float32)
    transformed = cv2.perspectiveTransform(point, H)

    rx = transformed[0][0][0]
    ry = transformed[0][0][1]

    return rx, ry


##############################################################################################
# Test Calibration
##############################################################################################
def test_transformation():

    H = load_homography()
    if H is None:
        return False

    if not os.path.exists(IMAGE_PATH):
        print("Captured image not found.")
        return False

    img = cv2.imread(IMAGE_PATH)

    def click_test(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            rx, ry = pixel_to_robot(x, y, H)
            print(f"Pixel ({x}, {y}) → Robot ({rx:.2f}, {ry:.2f})")

    print("Click anywhere on image to see robot coordinates.")

    cv2.imshow("Test Image", img)
    cv2.setMouseCallback("Test Image", click_test)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return True


##############################################################################################
# Main
##############################################################################################
def main():

    # # Step 1
    # capture_image()
    # # Step 2
    # collect_image_points()
    # # Step 3
    # generate_homography()
    # # Step 4
    # test_transformation()
    return None

if __name__ == "__main__":
    main()