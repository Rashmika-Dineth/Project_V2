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
from perception.object_detection import get_targets
import json
from time import sleep

##############################################################################################
# Global variables
##############################################################################################

dashboard, move, feed, feed_thread = None, None, None, None
ROBOT_IP = "192.168.1.6"
HOME_POINT = [350, 0, 0, 0]
DROP_POINT = [227, -243, -80, -83]
SAFE_Z_OFFSET = 80
robot_calibration_point_file = "./outputs/robot_calibration_points.json"
 
##############################################################################################
# Load the Json file
##############################################################################################
def Load_DROP_Data():
    global DROP_POINT, DROP_POINT_UP
    print("\nUpdating Dropoff location robot calibration data...")
    with open(robot_calibration_point_file, "r") as f:
         data = json.load(f)
         DROP_POINT = [data["point6"]["x"], data["point6"]["y"], data["point6"]["z"], data["point6"]["rx"], data["point6"]["ry"], data["point6"]["rz"]]
         DROP_POINT_UP = [data["point6"]["x"], data["point6"]["y"], data["point6"]["z"] + SAFE_Z_OFFSET, data["point6"]["rx"], data["point6"]["ry"], data["point6"]["rz"]]
        #  DROP_POINT[0] = data["point6"]["z"]
        #  DROP_POINT[1] = data["point6"]["z"]
        #  DROP_POINT[2] = data["point6"]["z"]
        #  DROP_POINT[3] = data["point6"]["rx"]
        #  DROP_POINT[4] = data["point6"]["ry"]
        #  DROP_POINT[5] = data["point6"]["rz"]
         return True


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

        Load_DROP_Data()


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
# Read and Save Calibration Points (CMD)
##############################################################################################
def Get_Robot_Calibration_Point_UI():
    current_pos = GetCurrentPosition()

    return {
        "x": round(float(current_pos[0]), 2),
        "y": round(float(current_pos[1]), 2),
        "z": round(float(current_pos[2]), 2),
        "rx": round(float(current_pos[3]), 2),
        "ry": round(float(current_pos[4]), 2),
        "rz": round(float(current_pos[5]), 2),
    }

def Save_Calibration_Points_UI(points, file_path):
    with open(file_path, "w") as f:
        json.dump(points, f, indent=4)

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
# Object Pick and Place
##############################################################################################
def Object_Pick_and_Place(color=None,shape=None):

    try:
        # Get selection from app buttons (CHANGE HERE)
        selected_color = color      # Example
        selected_shape = shape       # Example

        targets = get_targets(selected_color, selected_shape)

        

        print(f"\nFound {len(targets)} objects to pick")

        if len(targets) == 0:
            print("No matching objects found.")
            return

        # Move to Home first
        Move_Robot_To_Position_J(HOME_POINT)

        # =========================
        # PICK AND PLACE LOOP
        # =========================
        for i, (high, low) in enumerate(targets):

            print(f"\nPicking object {i+1}")

            # Approach
            Move_Robot_To_Position_J(high)
            status = Move_Robot_To_Position_J(low)
            # Pick (vacuum ON)
            status == True and Activate_Digital_Output(status=1)
            # Lift
            Move_Robot_To_Position_J(high)
            # Move to drop
            Move_Robot_To_Position_J(DROP_POINT_UP)
            Move_Robot_To_Position_J(DROP_POINT)
            Activate_Digital_Output(status=0)  
            Move_Robot_To_Position_J(DROP_POINT_UP)

        # Return Home after finishing
        Move_Robot_To_Position_J(HOME_POINT)   

    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        Disconnect_Robot()

    except Exception as e:
        print(f"\nERROR: {e}")
        Disconnect_Robot()


def main():
    return None

if __name__ == "__main__":
    main()