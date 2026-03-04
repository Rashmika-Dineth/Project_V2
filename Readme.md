# Machine Vision – Final Project Report

# Integrated Vision-Guided Robotic Pick-and-Place System

**1. Introduction**

This project presents the design and implementation of a complete vision-guided robotic
pick-and-place system, integrating camera-based object detection with a Dobot MG
industrial robot. The objective was to combine previously developed course components
image preprocessing, segmentation, coordinate mapping, and object selection into a
robust and usable end to end system.

The final system enables a camera to detect objects placed on a table, compute their real-
world coordinates using homography based calibration, and command the robot to pick
and place selected objects into a designated box. The system provides both a command-
line interface (CLI) and a graphical user interface (GUI) designed for factory operators.

**2. System Architecture and Integration**

The system was implemented using modular architecture to ensure maintainability and
independent testing of each subsystem. The main modules are:

- Calibration module
- Perception (vision) module
- Robot control module
- CLI interface
- Streamlit-based GUI
- Output

The overall processing pipeline is:

1. Camera image acquisition
2. Image preprocessing and segmentation
3. Object detection and center extraction (u, v)
4. Homography-based transformation to robot coordinates (X, Y)
5. Plan or Execute action

This modular separation allowed each component to be validated independently before
full system integration.

**3. Camera-to-Robot Calibration**

A dedicated calibration application was developed to compute the homography matrix
between the image plane and the robot workplane.

**3.1 Calibration Procedure**

The calibration process includes:

- Capturing an image from the real camera
- Selecting four-pixel coordinates (u, v) and save them in a json file
- Recording corresponding robot coordinates (X, Y) on the table plane and save them
  in a json file
- Computing a 3×3 homography matrix H
- Saving the calibration results into H_matrix.json

The JSON files for the calibration contains:

- Homography matrix H
- Image calibration points
- Robot calibration points

The calibration file is loaded automatically during detection and picking. This design avoids
repeated calibration and improves usability.

The accuracy of object placement strongly depends on calibration precision. Small errors
in point selection directly affect the mapping quality.

Capturing image from the robot actual coordinates

This need to replace with image

**Capture the real drop off location and get the real pick z location**

**Keep the path variables separate**

**4. Vision-to-Robot Mapping Pipeline**

The perception module detects objects using classical image processing techniques.

**4.1 Image Processing Steps**

1. Image acquisition
2. Gaussian blurring
3. Thresholding or color-based segmentation
4. Object shape detection
5. Object center computation

For each detected object, the pixel center (u, v) is calculated. The homography matrix H is
then applied:

```
(𝑋,𝑌, 1 )𝑇=𝐻⋅(𝑢,𝑣, 1 )𝑇
```

The resulting (X, Y) coordinates are used as robot targets.

**4.2 Optional Object Selection**

The system supports optional filtering by:

- **Color** (e.g., red, blue, yellow objects)
- **Shape** (e.g., circle, square, rectangle)
- Combined logic (e.g., blue circles)

This increases flexibility and simulates industrial sorting tasks.

**4.3 Output Visualization**

The system generates an annotated overlay image that includes:

- Object center marker
- Pixel coordinates
- Converted robot coordinates

In CLI mode, this image is saved to disk.
In GUI mode, it is displayed directly to the operator.

**5. Plan Mode vs Execute Mode**

A key design requirement was safe separation between simulation and real robot motion.

**Plan Mode (Without Dobot Connection)**

- Detect objects
- Compute and display (X, Y) coordinates
- Generate overlay image
- Do not move the robot

Plan mode allows validation of detection and coordinate mapping without risk.

**Execute Mode (Execution After Dobot connection)**

- Perform full pick-and-place sequence
- Move robot to target
- Activate gripper
- Move to drop location
- Release object

Execute mode is gated:

- CLI requires explicit --mode execute
- GUI requires Execute toggle and confirmation

This design ensures operational safety.

**6. Command-Line Interface (CLI)**

The CLI provides full system functionality and was implemented as the mandatory operator
interface.

Example usage:

python main.py

The CLI:

- Loads calibration automatically
- Prints pixel and robot coordinates
- Displays number of targets found
- Saves annotated overlay images
- Provides clear status messages

The interface was designed to be simple, readable, and safe.

**7. Graphical User Interface (GUI)**

A Streamlit-based GUI was developed to simulate a factory operator panel.

The GUI provides:

- Live or refreshed camera image
- Mode selection (Plan / Execute)
- Optional color and shape dropdown selection
- Buttons:
  o Capture / Refresh
  o Detect Target
  o Run Pick (enabled only in Execute mode)

The interface displays:

- Annotated image overlay
- Computed robot coordinates
- Clear feedback messages

The GUI improves usability compared to the CLI and better represents real industrial
systems.

**8. System Performance and Evaluation**

The system successfully integrates calibration, perception, coordinating transformation,
and robot control.

**Detection performance:**

- Reliable under moderate lighting conditions
- Sensitive to strong shadows and reflections

**Mapping accuracy:**

- Dependent on calibration quality
- Small millimeter-level errors observed due to manual point selection

**Execution performance:**

- Smooth robot movement
- Clear separation between simulation and physical motion

Overall, the system performs reliably for controlled laboratory conditions.

**9. Discussion**

The integration phase required careful debugging of coordinate frames and communication
between modules. The most challenging aspects were:

- **Connecting and communicating with DOBOT using the Python API:**
  There were some issues when trying to connect to DOBOT using the provided API.
  Although the ping command was successful and the DOBOT communicated
  properly with the DOBOT application, some DOBOT devices rejected the API
  connection itself. The application was also developed to maintain the connection
  with the DOBOT during program execution and to disconnect once the program is
  completed or terminated by the user.
- **Implementing safe execution with separate modules:**
  Some modules had to be kept separate, and due to the folder structure, there were
  missing path errors that took additional time to troubleshoot.
- **Color and shape detection:**
  The results were affected by lighting conditions, filtering methods, the type of
  module, and the mask used. It was also identified that different camera types
  produce different outputs. In some cases, squares were detected as polygons;
  however, this error was minimized by optimizing the shape detection code.
- **Camera quality:**
  During the image capture process, the Streamlit camera was initially planned for
  use with the web interface. However, the OpenCV camera provided better filtering
  and overall performance compared to the Streamlit camera. Therefore, the code
  was developed using OpenCV for image capture.

The project demonstrated how individual computer vision techniques become significantly
more complex when integrated into a real robotic system.

From a practical perspective, the system is functional but could be improved by:

- Automatic chessboard-based calibration
- Improved illumination control
- Multi-object trajectory optimization
- Error recovery mechanisms
  The development process provided valuable insight into real-world industrial automation
  challenges.

**10. Conclusion**

This project successfully implemented a complete vision-guided robotic pick-and-place
system using camera calibration, object detection, coordinate mapping, and robotic
control.

Both CLI and GUI interfaces operate correctly, and the Plan/Execute mode separation
ensures safety and usability. The modular architecture supports further expansion and
industrial adaptation.

The project demonstrates the practical application of machine vision techniques in robotic
automation systems.
