import subprocess
import sys
import robot.robot as robot

target_point = [350, 0, 0, 0]

##############################################################################################

def run_streamlit():
    subprocess.run(["streamlit", "run", "ui/ui.py"])

def main():
    print("==================================================================================")
    print("Welcome to the Machine Vision Project!")
    print("==================================================================================")
    print("1. Connect to Dobot MG400 Robot")
    print("2. Disconnect from Dobot MG400 Robot")
    print("3. Get Robot Calibration Points")
    print("4. Run Robot Movement")
    print("5. Run Streamlit UI")
    print("6. Exit")
    print("==================================================================================")

    choice = input("Please select an option (1-6): ")

    switch = {
        '1': lambda: (robot.Connect_Robot()),
        '2': lambda: (robot.Disconnect_Robot()),
        '3': lambda: (robot.Get_Robot_Calibration_Points()),
        '4': lambda: (robot.Move_Robot_To_Position_L(target_point)),
        # '5': run_streamlit,
        '6': lambda: sys.exit("Exiting program. Goodbye!")

    }

    func = switch.get(choice, lambda: print("Invalid option. Please select 1-6."))

    try:
        func()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.") 

if __name__ == "__main__":
    while True:
        main()
