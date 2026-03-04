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

robot_calibration_point_file = "robot_calibration_points.json"

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

if "calibration_step" not in st.session_state:
    st.session_state.calibration_step = 0

if "calibration_points" not in st.session_state:
    st.session_state.calibration_points = {}

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
    try:
        with st.spinner("Running calibration..."):

            calibration.capture_image()
            calibration.collect_image_points()

            # robot.Get_Robot_Calibration_Point_UI()
            # robot.Save_Calibration_Points_UI(st.session_state.calibration_points, robot_calibration_point_file)
            calibration.generate_homography()

        st.success("Calibration completed.")

    except Exception as e:
        st.error(f"Calibration failed: {str(e)}")

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



# ============================================================
# RIGHT PANEL – VISION SYSTEM
# ============================================================

with col2:
    st.subheader("�️ Vision System")
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
# Footer Status
# ============================================================
st.markdown("---")
if st.session_state.robot_connected:
    st.success("🟢 Robot Status: Connected")
else:
    st.error("🔴 Robot Status: Disconnected")
st.markdown("---")

st.subheader("👁️ Vision System")
col1, col2, col3 = st.columns(3)
st.markdown("---")
with col1:
    try:
        st.image("outputs/captured_img.png", caption="Captured Image", width=500)
    except:
        st.warning("Captured image not found.")
with col2:
    try:
        st.image("outputs/annotated_img.png", caption="Annotated Image", width=500) 
    except:
        st.warning("Annotated image not found.")
with col3:    
    try:
        st.image("outputs/final_marked_img.png", caption="Marked Annotated Image", width=500)
    except:
        st.warning("Marked annotated image not found.")
