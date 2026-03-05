import streamlit as st
from PIL import Image
import os
import sys
from time import sleep

# --------------------------------------------------
# Import project modules
# --------------------------------------------------

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import calibration.calibration as calibration
import robot.robot as robot
import perception.object_detection as object_detection


# --------------------------------------------------
# Page config
# --------------------------------------------------

st.set_page_config(
    page_title="Dobot MG400 Machine Vision",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Dobot MG400 Machine Vision Dashboard")
st.markdown("---")


# --------------------------------------------------
# Core Functions (Same as CLI)
# --------------------------------------------------

def calibrate():
    st.info("Starting calibration...")

    calibration.capture_image()
    calibration.collect_image_points()

    sleep(0.2)
    robot.Dashboard(False)
    sleep(0.2)
    robot.Get_Robot_Calibration_Points()
    sleep(0.2)
    st.info("Generating homography matrix...")
    robot.Dashboard(True)
    sleep(0.5)
    calibration.generate_homography()

    st.success("Calibration completed successfully.")


def detect(mode, color=None, shape=None):

    st.write(f"Detection mode: {mode}")
    st.write(f"Color filter: {color}")
    st.write(f"Shape filter: {shape}")

    if mode == "plan":

        with st.spinner("Capturing image and detecting objects..."):

            calibration.capture_image()

            object_detection.save_objects_with_robot_coordinates(color, shape)

            object_detection.mark_coordinates_on_annotated_image()

            robot.Load_DROP_Data()

        st.success("Detection planning completed.")

    elif mode == "execute":

        with st.spinner("Executing robot tasks..."):
            robot.Load_DROP_Data()
            robot.Object_Pick_and_Place()
            sleep(0.2)
        st.success("Detection execution completed.")

    else:
        st.error(f"Unknown mode: {mode}")


def pick(mode, color=None, shape=None):

    # robot.Connect_Robot()
    sleep(1)
    st.write(f"Pick mode: {mode}")
    st.write(f"Color filter: {color}")
    st.write(f"Shape filter: {shape}")

    if mode != "execute":
        st.warning("Pick command supports only execute mode.")
        return

    with st.spinner("Robot picking objects..."):

        robot.Load_DROP_Data()
        
        sleep(0.2)
        value = robot.Object_Pick_and_Place(color, shape)
        if value == False:
                st.warning("No matching objects found.")
        # robot.Dashboard(False)
        sleep(0.2)

    st.success("Pick execution completed.")
    # robot.Disconnect_Robot()
    sleep(1)

# --------------------------------------------------
# Layout
# --------------------------------------------------

left_col, right_col = st.columns(2)

# --------------------------------------------------
# LEFT PANEL – Calibration + Detection
# --------------------------------------------------

with left_col:

    st.subheader("⚙️ Calibration")

    if st.button("Robot Connect", use_container_width=True):
        sleep(0.1)
        robot.Connect_Robot()
        sleep(0.1)

    if st.button("Robot Disconnect", use_container_width=True):
        robot.Disconnect_Robot()

    if st.button("Run Calibration", use_container_width=True):
        robot.Dashboard(False)
        sleep(0.5)
        calibrate()
        robot.Dashboard(True)
        sleep(0.5)

    st.markdown("---")

    st.subheader("👁 Object Detection")

    detect_color_option = st.selectbox(
        "Select Color",
        ["All", "red", "green", "blue", "yellow"],
        key="detect_color"
    )

    detect_shape_option = st.selectbox(
        "Select Shape",
        ["All", "circle", "square", "triangle"],
        key="detect_shape"
    )

    detect_color = None if detect_color_option == "All" else detect_color_option
    detect_shape = None if detect_shape_option == "All" else detect_shape_option

    if st.button("Plan Detection", use_container_width=True):
        robot.Dashboard(False)
        sleep(0.5)
        detect("plan", detect_color, detect_shape)
        sleep(0.5)  
        robot.Dashboard(True)


    if st.button("Execute Detection Plan", use_container_width=True):
        detect("execute")


# --------------------------------------------------
# RIGHT PANEL – Pick and Place
# --------------------------------------------------

with right_col:

    st.subheader("📦 Pick and Place")

    pick_color_option = st.selectbox(
        "Select Color",
        ["All", "red", "green", "blue", "yellow"],
        key="pick_color"
    )

    pick_shape_option = st.selectbox(
        "Select Shape",
        ["All", "circle", "square", "triangle"],
        key="pick_shape"
    )

    pick_color = None if pick_color_option == "All" else pick_color_option
    pick_shape = None if pick_shape_option == "All" else pick_shape_option

    if st.button("Start Pick and Place", use_container_width=True):
        pick("execute", pick_color, pick_shape)


# --------------------------------------------------
# Vision Output Images
# --------------------------------------------------

st.markdown("---")
st.subheader("📷 Vision Output")

col1, col2, col3 = st.columns(3)

def show_image(path, title):
    if os.path.exists(path):
        img = Image.open(path)
        st.image(img, caption=title, use_column_width=True)
    else:
        st.warning(f"{title} not found.")


st.markdown("---")
st.subheader("👁 Vision Output")

def show_image(path, caption, width="content"):
    st.image(path, caption=caption, width=width)

img_col1, img_col2, img_col3 = st.columns(3)

with img_col1:
    show_image("outputs/captured_img.png", "Captured Image", width="stretch")

with img_col2:
    show_image("outputs/annotated_img.png", "Annotated Image", width="stretch")

with img_col3:
    show_image("outputs/final_marked_img.png", "Marked Annotated Image", width="stretch")