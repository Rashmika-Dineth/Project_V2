# Integrated Vision-Guided Robotic Pick-and-Place System

## Machine Vision – Final Project

### 📌 Overview

This project implements a complete vision-guided robotic pick-and-place system integrating camera-based object detection with a Dobot MG400 industrial robot.

The system combines:

Image preprocessing

Object segmentation

Homography-based coordinate mapping

Robot control

CLI and GUI interfaces

The final solution enables automatic detection of objects on a table and commands the robot to pick and place selected objects into a designated drop box.

### 🏗 System Architecture

The system follows a modular architecture for maintainability and independent testing.

Main Modules

Calibration Module

Perception (Vision) Module

Robot Control Module

Command-Line Interface (CLI)

Streamlit-Based GUI

Output Visualization Module

Processing Pipeline

Camera image acquisition

Image preprocessing & segmentation

Object detection and pixel center extraction (u, v)

Homography transformation → robot coordinates (X, Y)

Plan or Execute action

This modular design allows each component to be validated independently before full integration.

### 📐 Camera-to-Robot Calibration

A dedicated calibration application computes the homography matrix between the image plane and the robot workplane.

Calibration Procedure

Capture image from camera

Select four pixel coordinates (u, v)

Record corresponding robot coordinates (X, Y)

Compute 3×3 homography matrix H

Save results to:

outputs/H_matrix.json

Example calibration file:
https://github.com/Rashmika-Dineth/Project_V2/blob/main/outputs/H_matrix.json

Calibration File Contains

Homography matrix H

Image calibration points

Robot calibration points

⚠ Calibration accuracy directly affects mapping precision.

### 🎯 Vision-to-Robot Mapping Pipeline

Image Processing Steps

Image acquisition

Gaussian blurring

Thresholding / color-based segmentation

Shape detection

Object center computation

For each detected object:

(X, Y, 1)ᵀ = H · (u, v, 1)ᵀ

The computed (X, Y) coordinates are used as robot targets.

### 🎨 Object Selection (Optional Filtering)

The system supports filtering by:

Color: red, blue, yellow

Shape: circle, square, rectangle

Combined logic: e.g., blue circles

This simulates industrial sorting tasks.

### 🖼 Output Visualization

The system generates an annotated overlay image containing:

Object center marker

Pixel coordinates

Converted robot coordinates

In CLI mode → Image saved to disk

In GUI mode → Displayed directly to operator

### 🔐 Plan Mode vs Execute Mode

Safety was a key design requirement.

🧪 Plan Mode (Simulation)

Detect objects

Compute coordinates

Generate overlay image

❌ No robot movement

Used for validation without risk.

🤖 Execute Mode (Real Robot)

Full pick-and-place sequence

Move to target

Activate gripper

Move to drop location

Release object

Safety Gating

CLI requires:

--mode execute

GUI requires:

Execute toggle

Confirmation action

### 💻 Command-Line Interface (CLI)

The CLI is the mandatory operator interface.

Run:
python main.py
CLI Features

Automatic calibration loading

Prints pixel & robot coordinates

Displays number of targets

Saves annotated overlay image

Clear status messages

Designed to be simple, readable, and safe.

### 🖥 Graphical User Interface (GUI)

A Streamlit-based GUI simulates a factory operator panel.

GUI Features

Live / refreshed camera image

Mode selection (Plan / Execute)

Color & shape dropdown filters

Buttons:

Capture / Refresh

Detect Target

Run Pick (enabled only in Execute mode)

GUI Displays

Annotated image overlay

Computed robot coordinates

Status and feedback messages

The GUI improves usability and better reflects real industrial systems.

### 📊 System Performance

Detection Performance

Reliable under moderate lighting

Sensitive to shadows & reflections

Mapping Accuracy

Dependent on calibration quality

Millimeter-level errors due to manual point selection

Execution Performance

Smooth robot motion

Clear separation between simulation and physical execution

System performs reliably under controlled lab conditions.

### ⚙ Challenges & Discussion

🔌 Dobot API Connectivity

Some devices rejected API connection

Connection management implemented (connect → maintain → disconnect)

🗂 Modular Structure & Path Issues

Folder structure caused path errors during integration

Resolved by separating path variables clearly

🎨 Color & Shape Detection

Lighting conditions affected results

Some squares detected as polygons

Optimized shape detection to reduce errors

📷 Camera Choice

Streamlit camera initially tested

OpenCV camera provided better filtering & performance

Final implementation uses OpenCV for image capture

### 🚀 Future Improvements

Automatic chessboard-based calibration

Improved illumination control

Multi-object trajectory optimization

Error recovery mechanisms

### 🏁 Conclusion

This project successfully implements a complete vision-guided robotic pick-and-place system integrating:

Camera calibration

Object detection

Coordinate transformation

Robotic control

The system includes both CLI and GUI interfaces with a clear Plan/Execute safety separation.

The modular architecture supports future expansion and industrial adaptation.

This project demonstrates the practical application of machine vision in robotic automation systems.
