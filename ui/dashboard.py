import streamlit as st
from PIL import Image
import os
import sys
from time import sleep

# ============================================================
# Import Project Modules
# ============================================================

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import calibration.calibration as calibration
import robot.robot as robot
import perception.object_detection as object_detection

# ============================================================
# Page Config
# ============================================================

st.set_page_config(
    page_title="Dobot MG400 - Machine Vision",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Dobot MG400 Machine Vision Dashboard")
st.markdown("---")

# ============================================================
# Session State
# ============================================================

if "robot_connected" not in st.session_state:
    st.session_state.robot_connected = False

# ============================================================
# Helper Functions
# ============================================================

def connect_robot():
    try:
        robot.Connect_Robot()
        st.session_state.robot_connected = True
        st.success("Robot connected successfully.")
    except Exception as e:
        st.error(f"Failed to connect robot: {e}")


def disconnect_robot():
    try:
        robot.Disconnect_Robot()
        st.session_state.robot_connected = False
        st.warning("Robot disconnected.")
    except Exception as e:
        st.error(f"Failed to disconnect robot: {e}")


def run_calibration():
    try:
        with st.spinner("Running calibration..."):

            calibration.capture_image()
            calibration.collect_image_points()

            sleep(0.2)

            robot.Connect_Robot()
            robot.Dashboard(False)

            sleep(0.2)

            robot.Get_Robot_Calibration_Points()

            sleep(0.2)

            robot.Disconnect_Robot()

            sleep(0.5)

            calibration.generate_homography()

        st.success("Calibration completed successfully.")

    except Exception as e:
        st.error(f"Calibration failed: {str(e)}")


def run_detection(color=None, shape=None):
    try:
        with st.spinner("Capturing and detecting objects..."):

            calibration.capture_image()

            object_detection.save_objects_with_robot_coordinates(color, shape)

            object_detection.mark_coordinates_on_annotated_image()

            robot.Load_DROP_Data()

        st.success("Object detection completed.")

    except Exception as e:
        st.error(f"Detection failed: {str(e)}")


def run_pick_and_place(color=None, shape=None):
    try:
        with st.spinner("Running Pick and Place..."):

            robot.Connect_Robot()

            robot.Load_DROP_Data()

            sleep(0.3)

            value = robot.Object_Pick_and_Place(color=color, shape=shape)

            sleep(0.3)

            robot.Disconnect_Robot()

            if value == False:
                st.warning("No matching objects found.")

        st.success("Pick and Place completed.")

    except Exception as e:
        st.error(f"Pick and Place failed: {str(e)}")


def show_image(image_path, title):
    if os.path.exists(image_path):
        img = Image.open(image_path)
        st.image(img, caption=title, use_column_width=True)
    else:
        st.warning(f"{title} not found.")


# ============================================================
# Layout
# ============================================================

left_col, right_col = st.columns(2)

# ============================================================
# LEFT PANEL – ROBOT CONTROL + DETECTION
# ============================================================

with left_col:

    st.subheader("🔌 Robot Control")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Connect Robot", use_container_width=True):
            connect_robot()

    with col2:
        if st.button("Disconnect Robot", use_container_width=True):
            disconnect_robot()

    st.markdown("---")

    if st.button("Run Calibration", use_container_width=True):
        run_calibration()

    st.markdown("---")

    st.subheader("👁 Vision System")

    detect_color_option = st.selectbox(
        "Select Color (optional)",
        ["All", "red", "green", "blue", "yellow"]
    )

    detect_shape_option = st.selectbox(
        "Select Shape (optional)",
        ["All", "circle", "square", "triangle"]
    )

    detect_color = None if detect_color_option == "All" else detect_color_option
    detect_shape = None if detect_shape_option == "All" else detect_shape_option

    if st.button("Start Object Detection", use_container_width=True):
        run_detection(detect_color, detect_shape)


# ============================================================
# RIGHT PANEL – PICK AND PLACE
# ============================================================

with right_col:

    st.subheader("📦 Picking System")

    pick_color_option = st.selectbox(
        "Select Color (optional)",
        ["All", "red", "green", "blue", "yellow"]
    )

    pick_shape_option = st.selectbox(
        "Select Shape (optional)",
        ["All", "circle", "square", "triangle"]
    )

    pick_color = None if pick_color_option == "All" else pick_color_option
    pick_shape = None if pick_shape_option == "All" else pick_shape_option

    if st.button("Start Pick and Place", use_container_width=True):
        run_pick_and_place(pick_color, pick_shape)

# ============================================================
# Vision Output Images
# ============================================================

st.markdown("---")
st.subheader("👁 Vision Output")

img_col1, img_col2, img_col3 = st.columns(3)

with img_col1:
    show_image("outputs/captured_img.png", "Captured Image")

with img_col2:
    show_image("outputs/annotated_img.png", "Annotated Image")

with img_col3:
    show_image("outputs/final_marked_img.png", "Marked Annotated Image")