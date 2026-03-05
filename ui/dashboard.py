import streamlit as st
from PIL import Image
import os
import sys
from time import sleep

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
        st.success("Robot connected successfully.")
    except Exception as e:
        st.error(f"Failed to connect to robot")


def disconnect_robot():
    try:        
        robot.Disconnect_Robot()
        st.warning("Robot disconnected.")
    except Exception as e:
        st.error(f"Failed to disconnect from robot")


def run_detection():
    with st.spinner("Capturing and detecting objects..."):
        robot.Dashboard(enable=False) 
        sleep(0.2)
        calibration.capture_image()
        object_detection.save_objects_with_robot_coordinates(color=None,shape=None)
        object_detection.mark_coordinates_on_annotated_image()
        robot.Dashboard(enable=True) 
        sleep(0.2)
    st.success("Detection completed.")


def run_pick_and_place(color, shape):
    with st.spinner("Running Pick and Place..."):
        robot.Connect_Robot()
        robot.Load_DROP_Data()
     # Disable robot during object detection
        # calibration.capture_image()
        # object_detection.save_objects_with_robot_coordinates()
        # object_detection.mark_coordinates_on_annotated_image()
        sleep(0.3)
        value = robot.Object_Pick_and_Place(color=color, shape=shape)
        sleep(0.3)
        robot.Disconnect_Robot()
        sleep(0.3)
        if value == False:
            st.error("No matching objects")
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
            robot.Dashboard(enable=False) 
            sleep(0.2)
            calibration.capture_image()
            calibration.collect_image_points()

            # robot.Get_Robot_Calibration_Point_UI()
            # robot.Save_Calibration_Points_UI(st.session_state.calibration_points, robot_calibration_point_file)
            calibration.generate_homography()
            robot.Dashboard(enable=True) 
            sleep(0.2)
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

    if st.button("Connect Robot", use_container_width=True):
            connect_robot()
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
        ["All", "red", "green", "blue", "yellow"]
    )

    shape_option = st.selectbox(
        "Select Shape (optional)",
        ["All", "circle", "square", "triangle"]
    )

    selected_color = None if color_option == "All" else color_option
    selected_shape = None if shape_option == "All" else shape_option

    if st.button("Start Pick and Place", use_container_width=True):
        
        run_pick_and_place(selected_color, selected_shape)
        


# ============================================================
# Footer Status
# ============================================================
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
