import cv2
import numpy as np
import json
import os

##############################################################################################
# Import your class from the other file
##############################################################################################
from perception.colshap import ShapeColorDetector

##############################################################################################
# File paths
##############################################################################################
IMAGE_PATH = "./outputs/captured_img.png"
H_MATRIX_PATH = "./outputs/H_matrix.json"
OUTPUT_JSON_PATH = "./outputs/detected_objects.json"
OUTPUT_ANNOTATED_IMAGE = "./outputs/annotated_img.png"
OUTPUT_ANNOTATED_IMAGE_CENTER="./outputs/mapping_visualized.png"
robot_calibration_point_file = "./outputs/robot_calibration_points.json"

SAFE_Z_OFFSET = 60        # distance above object
PICK_Z = 0                # object surface height

##############################################################################################
# Load the Z data
##############################################################################################
def Load_Z_Data():
    global PICK_Z
    print("\nLoading robot calibration data...")
    with open(robot_calibration_point_file, "r") as f:
         data = json.load(f)
         PICK_Z = data["point5"]["z"]
         return PICK_Z

##############################################################################################
# Load homography matrix
##############################################################################################
def load_homography():
    if not os.path.exists(H_MATRIX_PATH):
        print("H matrix file not found.")
        return None
    with open(H_MATRIX_PATH, "r") as f:
        H = np.array(json.load(f))
    return H

##############################################################################################
# Pixel to robot coordinate transformation
##############################################################################################
def pixel_to_robot(x, y, H):
    point = np.array([[[x, y]]], dtype=np.float32)
    transformed = cv2.perspectiveTransform(point, H)
    rx = float(transformed[0][0][0])
    ry = float(transformed[0][0][1])
    return rx, ry

##############################################################################################
# Detect objects and save with robot coordinates
##############################################################################################
def save_objects_with_robot_coordinates():

    image = cv2.imread(IMAGE_PATH)
    if image is None:
        print("Image not found:", IMAGE_PATH)
        return

    H = load_homography()
    if H is None:
        return

    detector = ShapeColorDetector()
    objects = detector.detect(image)

    output_data = {}
    object_count = 1

    #############################################
    # Detect objects
    #############################################
    for obj in objects:

        cx, cy = obj["center"]
        rx, ry = pixel_to_robot(cx, cy, H)

        output_data[f"object{object_count}"] = {
            "shape": obj["shape"],
            "color": obj["color"],
            "image": {
                "x": float(cx),
                "y": float(cy)
            },
            "robot": {
                "x": rx,
                "y": ry
            }
        }

        object_count += 1

    os.makedirs("output", exist_ok=True)

    with open(OUTPUT_JSON_PATH, "w") as f:
        json.dump(output_data, f, indent=4)

    print("Saved robot object data to:", OUTPUT_JSON_PATH)

    #############################################
    # Annotate and save image
    #############################################
    annotated = detector.annotate(image, objects)

    cv2.imwrite(OUTPUT_ANNOTATED_IMAGE, annotated)
    print("Saved annotated image to:", OUTPUT_ANNOTATED_IMAGE)

    cv2.imshow("Detected with Robot Mapping", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


##############################################################################################
# Visualize image-robot mapping
##############################################################################################
def mark_coordinates_on_annotated_image(
        image_path=OUTPUT_ANNOTATED_IMAGE,
        json_path=OUTPUT_JSON_PATH,
        output_path="./outputs/final_marked_img.png"):

    image = cv2.imread(image_path)

    if image is None:
        print("Annotated image not found")
        return

    if not os.path.exists(json_path):
        print("JSON file not found")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    for key, obj in data.items():

        if key == "metadata":
            continue

        img_x = int(obj["image"]["x"])
        img_y = int(obj["image"]["y"])

        robot_x = float(obj["robot"]["x"])
        robot_y = float(obj["robot"]["y"])

        #################################
        # Draw red dot on image coordinate
        #################################
        cv2.circle(image, (img_x, img_y), 6, (0, 0, 255), -1)

        #################################
        # Display text
        #################################
        text = f"({img_x},{img_y}) -> ({robot_x:.2f},{robot_y:.2f})"

        cv2.putText(image, text, (img_x - 60, img_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, image)

    print("Marked image saved to:", output_path)

    cv2.imshow("Marked Coordinates", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

##############################################################################################
# Load the Json file
##############################################################################################
def load_objects():
    with open(OUTPUT_JSON_PATH, "r") as f:
        return json.load(f)

##############################################################################################
# Read detected objects based on color and shape and return target points for robot
##############################################################################################
def get_targets(selected_color=None, selected_shape=None):
    """
    Returns list of (high_point, low_point) tuples
    filtered by color and/or shape
    """
    data = load_objects()
    targets = []

    Load_Z_Data()

    for key, point in data.items():

        color_match = (selected_color is None) or (point["color"] == selected_color)
        shape_match = (selected_shape is None) or (point["shape"] == selected_shape)

        if color_match and shape_match:

            x = point["robot"]["x"]
            y = point["robot"]["y"]

            high_point = [x, y, PICK_Z + SAFE_Z_OFFSET, 0]
            low_point = [x, y, PICK_Z, 0]

            targets.append((high_point, low_point))


    return targets

##############################################################################################
# Main
##############################################################################################
def main():
    # save_objects_with_robot_coordinates(IMAGE_PATH)
    # mark_coordinates_on_annotated_image()
    # print(get_targets(None, selected_shape="polygon"))
    return True
if __name__ == "__main__":
    main()