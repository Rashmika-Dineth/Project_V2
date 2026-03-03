##############################################################################################
# Robot Movement
##############################################################################################
from robot.dobot_controller import (
    ConnectRobot,
    StartFeedbackThread,
    SetupRobot,
    MoveJ,
    MoveL,
    WaitArrive,
    ControlDigitalOutput,
    GetCurrentPosition,
    DisconnectRobot
)
import json
from time import sleep

##############################################################################################
# Global variables
##############################################################################################

dashboard, move, feed, feed_thread = None, None, None, None
ROBOT_IP = "192.168.1.6"
target_point = [350, 0, 0, 0]
robot_calibration_point_file = "robot_calibration_points.json"

##############################################################################################
# Connect to robot and setup
##############################################################################################
def Connect_Robot():
    global dashboard, move, feed, feed_thread
    global ROBOT_IP 
    
    try:
        # Connect to robot
        print("=" * 50)
        print("DOBOT MG400 CONTROL WITH VISION SYSTEM")
        print("=" * 50)
        dashboard, move, feed = ConnectRobot(ip=ROBOT_IP, timeout_s=5.0)
        
        # Start feedback monitoring thread
        feed_thread = StartFeedbackThread(feed)
        
        # Setup and enable robot
        SetupRobot(dashboard, speed_ratio=50, acc_ratio=50)
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
        DisconnectRobot(dashboard, move, feed, feed_thread)        
    except Exception as e:
        print(f"\n*** ERROR occurred: {e} ***")
        DisconnectRobot(dashboard, move, feed, feed_thread)        
        import traceback
        traceback.print_exc()

##############################################################################################
# Disconnect from robot
##############################################################################################
def Disconnect_Robot():
    global dashboard, move, feed, feed_thread
    try:
        DisconnectRobot(dashboard, move, feed, feed_thread)        
    except Exception as e:
        print(f"\n*** ERROR occurred during disconnect: {e} ***")
        import traceback
        traceback.print_exc()

##############################################################################################
# Read and Save Calibration Points (CMD)
##############################################################################################
def Get_Robot_Calibration_Points():
    try:
        calibration_points = {}

        for i in range(6):
            if i == 4:
                input("\nMove robot to on top of a tile and press Enter...")
            elif i == 5:
                input("\nMove robot to on top of the drop location and press Enter...")
            else:
                input(f"\nMove robot to point {i+1} and press Enter...")

            current_pos = GetCurrentPosition()

            x  = float(current_pos[0])
            y  = float(current_pos[1])
            z  = float(current_pos[2])
            rx = float(current_pos[3])
            ry = float(current_pos[4])
            rz = float(current_pos[5])

            print(f"Saved point{i+1}: {current_pos}")

            calibration_points[f"point{i+1}"] = {
                "x": round(x, 2),
                "y": round(y, 2),
                "z": round(z, 2),
                "rx": round(rx, 2),
                "ry": round(ry, 2),
                "rz": round(rz, 2)
            }

        with open(robot_calibration_point_file, "w") as f:
            json.dump(calibration_points, f, indent=4)

        print("\nCalibration points saved successfully.")

        return calibration_points

    except Exception as e:
        print(f"\n*** ERROR occurred: {e} ***")
        import traceback
        traceback.print_exc()
        return None

##############################################################################################
# Move robot to a target position Linearly
##############################################################################################
def Move_Robot_To_Position_L(target_point):
    global move
    MoveL(move, target_point)
    
    # Wait for robot to reach the point
    arrived = WaitArrive(target_point, tolerance=1.0, timeout=30.0)
    if arrived:
        return True
    else:
        return False

##############################################################################################
# Move robot to a target position Jointly
##############################################################################################
def Move_Robot_To_Position_J(target_point):
    global move
    MoveJ(move, target_point)

    # Wait for robot to reach the point
    arrived = WaitArrive(target_point, tolerance=1.0, timeout=30.0)
    if arrived:
        return True
    else:
        return False
    
##############################################################################################
# Activate the digital output
##############################################################################################
def Activate_Digital_Output(status=0):
    global dashboard, output_index
    ControlDigitalOutput(dashboard, output_index=output_index, status=status) 
    sleep(0.2)  # Wait for the command to execute
    return True
##############################################################################################
