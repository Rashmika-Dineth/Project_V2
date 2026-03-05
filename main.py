import argparse
from time import sleep

import calibration.calibration as calibration
import robot.robot as robot
import perception.object_detection as object_detection


def calibrate():
    print("Starting calibration...")
    robot.Dashboard(enable=False)

    calibration.capture_image()
    calibration.collect_image_points()
    robot.Get_Robot_Calibration_Points()

    print("Generating homography matrix...")
    sleep(0.5)

    calibration.generate_homography()

    print("Calibration completed successfully.")
    robot.Dashboard(enable=True)


def detect(mode, color=None, shape=None):
    print(f"[DETECT] mode={mode}, color={color}, shape={shape}")

    if mode == "plan":
        calibration.capture_image()
        object_detection.save_objects_with_robot_coordinates(color,shape)
        object_detection.mark_coordinates_on_annotated_image()
        robot.Load_DROP_Data()

        print("Detection planning completed.")

    elif mode == "execute":
        robot.Load_DROP_Data()
        robot.Connect_Robot()

        sleep(0.5)
        robot.Object_Pick_and_Place()

        sleep(0.2)
        robot.Disconnect_Robot()

        print("Detection execution completed.")

    else:
        print(f"Unknown mode: {mode}")


def pick(mode, color=None, shape=None):
    print(f"[PICK] mode={mode}, color={color}, shape={shape}")

    if mode != "execute":
        print("Pick command supports only execute mode.")
        return

    robot.Load_DROP_Data()
    robot.Connect_Robot()

    sleep(0.5)
    robot.Object_Pick_and_Place(color, shape)

    sleep(0.2)
    robot.Disconnect_Robot()

    print("Pick execution completed.")


def main():
    parser = argparse.ArgumentParser(description="CLI Tool")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---------- detect ----------
    parser_detect = subparsers.add_parser("detect")

    parser_detect.add_argument(
        "--mode",
        required=True,
        choices=["plan", "execute"]
    )

    # Optional filters
    parser_detect.add_argument("--color", required=False)
    parser_detect.add_argument("--shape", required=False)

    parser_detect.set_defaults(
        func=lambda args: detect(
            args.mode,
            args.color,
            args.shape
        )
    )

    # ---------- pick ----------
    parser_pick = subparsers.add_parser("pick")

    parser_pick.add_argument(
        "--mode",
        required=True,
        choices=["execute"]
    )

    parser_pick.add_argument("--color", required=False)
    parser_pick.add_argument("--shape", required=False)

    parser_pick.set_defaults(
        func=lambda args: pick(
            args.mode,
            args.color,
            args.shape
        )
    )

    # ---------- calibrate ----------
    parser_calibrate = subparsers.add_parser("calibrate")
    parser_calibrate.set_defaults(func=lambda args: calibrate())

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()