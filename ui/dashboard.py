import streamlit as st
from PIL import Image
import os
import sys

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
        st.error(f"Failed to connect to robot")


def disconnect_robot():
    try:        
        robot.Disconnect_Robot()
        st.session_state.robot_connected = False
        st.warning("Robot disconnected.")
    except Exception as e:
        st.error(f"Failed to disconnect from robot")


def run_detection():
    with st.spinner("Capturing and detecting objects..."):
        calibration.capture_image()
        object_detection.save_objects_with_robot_coordinates()
        object_detection.mark_coordinates_on_annotated_image()
    st.success("Detection completed.")


def run_pick_and_place(color, shape):
    with st.spinner("Running Pick and Place..."):
        robot.Object_Pick_and_Place(color=color, shape=shape)
    st.success("Pick and Place completed.")


def show_image(image_path, title):
    if os.path.exists(image_path):
        img = Image.open(image_path)
        st.image(img, caption=title, use_column_width=True)
    else:
        st.warning(f"{title} not found.")

def run_calibration():
    with st.spinner("Running calibration..."):
         calibration.capture_image()
         calibration.collect_image_points()
         robot.Get_Robot_Calibration_Points()
         calibration.generate_homography()
    st.success("Calibration completed.")

# ============================================================
# Layout
# ============================================================

col1, col2 = st.columns(2)

# ============================================================
# LEFT PANEL – ROBOT CONTROL
# ============================================================

with col1:
    st.subheader("🔌 Robot Control")

    if not st.session_state.robot_connected:
        if st.button("Connect Robot", use_container_width=True):
            connect_robot()
    else:
        if st.button("Disconnect Robot", use_container_width=True):
            disconnect_robot()

    if st.button("Calibration", use_container_width=True):
            run_calibration()

    if st.button("Run Object Detection", use_container_width=True):
            run_detection()

    st.markdown("---")
    st.subheader("📦 Pick & Place Filters")

    # Filtering Options
    color_option = st.selectbox(
        "Select Color (optional)",
        ["None", "red", "green", "blue", "yellow"]
    )

    shape_option = st.selectbox(
        "Select Shape (optional)",
        ["None", "circle", "square", "triangle"]
    )

    selected_color = None if color_option == "None" else color_option
    selected_shape = None if shape_option == "None" else shape_option

    if st.button("Start Pick and Place", use_container_width=True):
        if st.session_state.robot_connected:
            run_pick_and_place(selected_color, selected_shape)
        else:
            st.error("Please connect the robot first.")


# ============================================================
# RIGHT PANEL – VISION SYSTEM
# ============================================================

with col2:
    st.subheader("👁️ Vision System")

    st.subheader("🖼️ Image Viewer")
    
    if st.button("Show Captured Image"):
        st.image("outputs/captured_img.png", caption="Captured Image", width=500)

    if st.button("Show Annotated Image"):
        st.image("outputs/annotated_img.png", caption="Annotated Image", width=500)

    if st.button("Show Marked Annotated Image"):
        st.image("outputs/final_marked_img.png", caption="Marked Annotated Image", width=500)


# ============================================================
# Footer Status
# ============================================================

st.markdown("---")

if st.session_state.robot_connected:
    st.success("🟢 Robot Status: Connected")
else:
    st.error("🔴 Robot Status: Disconnected")