import cv2
import numpy as np
import json
import os

##############################################################################################
# Import your class from the other file
##############################################################################################
from colshap import ShapeColorDetector

##############################################################################################
# File paths
##############################################################################################
IMAGE_PATH = "./outputs/captured_img.png"
H_MATRIX_PATH = "./outputs/H_matrix.json"
OUTPUT_JSON_PATH = "./outputs/detected_objects.json"
OUTPUT_ANNOTATED_IMAGE = "./outputs/annotated_img.png"
OUTPUT_ANNOTATED_IMAGE_CENTER="./outputs/mapping_visualized.png"

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
def save_objects_with_robot_coordinates(image_path):

    image = cv2.imread(image_path)
    if image is None:
        print("Image not found:", image_path)
        return

    H = load_homography()
    if H is None:
        return

    detector = ShapeColorDetector()
    objects = detector.detect(image)

    output_data = {}
    object_count = 1

    #############################################
    # Image center coordinates
    #############################################
    h_img, w_img = image.shape[:2]

    image_center_pixel = (w_img / 2, h_img / 2)
    robot_center = pixel_to_robot(image_center_pixel[0],
                                  image_center_pixel[1],
                                  H)

    print("\n===== Image Center Info =====")
    print("Image center pixel (x,y):", image_center_pixel)
    print("Robot center coordinate (x,y):", robot_center)

    #############################################
    # Store metadata
    #############################################
    output_data["metadata"] = {
        "image_center": {
            "x": float(image_center_pixel[0]),
            "y": float(image_center_pixel[1])
        },
        "robot_center": {
            "x": float(robot_center[0]),
            "y": float(robot_center[1])
        }
    }

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

    # Draw image center point on annotation
    center_px = (int(image_center_pixel[0]), int(image_center_pixel[1]))
    cv2.circle(annotated, center_px, 6, (0, 0, 255), -1)
    cv2.putText(annotated, "Image Center",
                (center_px[0] + 10, center_px[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1)

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
# Main
##############################################################################################
def main():
    # save_objects_with_robot_coordinates(IMAGE_PATH)
    # mark_coordinates_on_annotated_image()
    return True
if __name__ == "__main__":
    main()