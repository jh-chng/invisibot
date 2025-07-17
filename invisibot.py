#!/usr/bin/env python3
import sys
import time
import argparse

# For debug
import traceback

import uvicorn
from fastapi import FastAPI
from utils.differential_drive import Invisibot
from utils.messages import Location, Request, Response

STANDALONE = False
app = FastAPI()


class ApiServer:
    """
    ApiServer class to create a FastAPI server for the Invisibot robot.
    This class initializes the robot with a given name, port, position (x, y, yaw), and floor.
    It sets up various endpoints to handle navigation, status, path requests, and control commands.
    The endpoints include:
    - /navigate_to_pose: Navigate the robot to a specified pose.
    - /status: Get the current status of the robot.
    - /stop: Stop the robot and simulate a connection loss.
    - /resume: Resume the robot's operations after a stop.

    """

    def __init__(self, robot_name, port, x, y, yaw, floor) -> None:
        self.ib = Invisibot(x, y, yaw, floor)
        self.robot_name = robot_name
        self.throwaway = None

        print(
            f"Invisibot [ {robot_name} ] spawned @ [ {x},{y},{yaw} ] at [ {floor} ] with port [ {port} ]"
        )
        print(
            f"Please access [ {robot_name} ] API Server at [ http://localhost:8080/docs ]"
        )

        @app.post("/navigate_to_pose", response_model=Response)
        async def nav(robot_name: str, dest: Location):
            print(f"/navigate_to_pose called {robot_name} {dest}")
            response = {
                "success": False,
                "msg": "Beep Boop Beep",
            }
            temp_dest = Request()
            temp_dest.map_name = dest.level_name
            if dest.level_name is None:
                print("Target floor name is None, using default floor")
                temp_dest.map_name = self.ib.floor
            temp_dest.destination = [dest]
            self.ib.move(dest.index, temp_dest)
            response["success"] = True
            return response

        @app.get("/status", response_model=Response)
        async def status():
            # print(f"/status called {robot_name}")
            response = {
                "success": False,
                "msg": "Beep Boop Beep",
            }

            data = {}
            data["robot_name"] = self.robot_name
            data["map_name"] = self.ib.floor
            data["position"] = {
                "x": self.ib.self_x,
                "y": self.ib.self_y,
                "yaw": self.ib.self_yaw,
            }
            data["battery"] = 100.0
            data["completed_request"] = not self.ib.move_flag
            data["destination_arrival"] = None
            data["curr_path_size"] = self.ib.curr_path
            data["last_completed_request"] = self.ib.cmd_id

            response["data"] = data

            return response

        @app.post("/map_switch", response_model=Response)
        async def map_switch(robot_name: str, map: str):
            print(f"/map_switch called {robot_name} from {self.ib.floor}->{map}")
            response = {
                "success": False,
                "msg": "Beep Boop Beep",
            }
            self.ib.floor = map
            response["success"] = True
            return response

        @app.post("/stop", response_model=Response)
        async def stop():
            response = {"data": {}, "success": False, "msg": ""}
            response["success"] = True
            self.ib.stop()
            print("Freezing all APIs to simulate a connection loss")
            time.sleep(30)
            print(f"Stop API called")
            return response

        @app.post("/resume", response_model=Response)
        async def resume():
            response = {"data": {}, "success": False, "msg": ""}
            response["success"] = True
            self.ib.resume()
            return response

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="warning",
        )


def main():
    parser = argparse.ArgumentParser(
        prog="invisibot", description="Configure and spin up the invisibot"
    )

    parser.add_argument(
        "-r", "--robot_name", type=str, default="robot1", help="Name of the robot"
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8080, help="Port to run the API server on"
    )
    parser.add_argument(
        "-l",
        "--location",
        type=str,
        default="0.0,0.0,0.0",
        help="Comma seperated location of the robot (x,y,yaw)",
    )
    parser.add_argument(
        "-m", "--map", type=str, default="L1", help="Current Map of the robot"
    )
    args = parser.parse_args()

    try:
        ApiServer(
            args.robot_name, args.port, *map(float, args.location.split(",")), args.map
        ).ib.start()

    except Exception as e:

        print(
            f"Error trying to open with error {e}. Try running with the -c or --help flag"
        )
        sys.exit(-1)
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
