#!/usr/bin/env python3
import sys
import json
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

    def __init__(self, port, robots_data) -> None:
        self.ib_fleet = []
        for robot_name in robots_data:

            x = robots_data[robot_name]["pose"]["x"]
            y = robots_data[robot_name]["pose"]["y"]
            yaw = robots_data[robot_name]["pose"]["yaw"]
            floor = robots_data[robot_name]["map_name"]
            
            robot = Invisibot(robot_name,x,y,yaw,floor)

            self.ib_fleet.append(robot)

            print(
                f"Invisibot [ {robot_name} ] spawned @ [ {x}, {y}, {yaw} ] at [ {floor} ]"
            )

        print(
            f"Please access Invisibot Fleet API Server at [ http://localhost:{port}/docs ]"
        )

        @app.get("/ping", response_model=Response)
        async def status():
            response = {}
            response["success"] = True
            response["msg"] = "Beep Boop Beep"

            return response

        @app.post("/navigate_to_pose", response_model=Response)
        async def nav(robot_name: str, dest: Location):
            print(f"/navigate_to_pose called {robot_name} {dest}")

            response = {}
            selected_ib = self.check_if_robot_exists(robot_name)
            if selected_ib is None:
                response = {
                    "success": False,
                    "msg": f"Error - [ {robot_name} ] does not exist.",
                }
                return response

            temp_dest = Request()
            temp_dest.map_name = dest.level_name

            if dest.level_name is None:
                print("Target floor name is None, using default floor")
                temp_dest.map_name = selected_ib.floor
            temp_dest.destination = [dest]
            selected_ib.move(dest.index, temp_dest)
            response["success"] = True
            response["msg"] = "Beep Boop Beep"

            return response

        @app.get("/status", response_model=Response)
        async def status(robot_name: str):
            response = {}
            selected_ib = self.check_if_robot_exists(robot_name)
            if selected_ib is None:
                response = {
                    "success": False,
                    "msg": f"Error - [ {robot_name} ] does not exist.",
                }
                return response

            data = {}
            data["robot_name"] = selected_ib.name
            data["map_name"] = selected_ib.floor
            data["position"] = {
                "x": selected_ib.current_x,
                "y": selected_ib.current_y,
                "yaw": selected_ib.current_yaw,
            }
            data["battery"] = 100.0
            data["completed_request"] = not selected_ib.is_moving
            data["destination_arrival"] = None
            data["curr_path_size"] = selected_ib.current_path_segment
            data["last_completed_request"] = selected_ib.current_command_id

            response["data"] = data
            response["success"] = True
            response["msg"] = "Beep Boop Beep"

            return response

        @app.post("/map_switch", response_model=Response)
        async def map_switch(robot_name: str, map: str):
            response = {}
            selected_ib = self.check_if_robot_exists(robot_name)
            if selected_ib is None:
                response = {
                    "success": False,
                    "msg": f"Error - [ {robot_name} ] does not exist. Switch map - [ FAIL ]",
                }
                return response
            
            print(f"/map_switch called {robot_name} from {selected_ib.floor} -> {map}")

            response["success"] = True
            response["msg"] = "Switch map - [ SUCCESS ]"
            selected_ib.floor = map

            return response

        @app.post("/stop", response_model=Response)
        async def stop(robot_name: str):

            response = {}
            selected_ib = self.check_if_robot_exists(robot_name)
            if selected_ib is None:
                response = {
                    "success": False,
                    "msg": f"Error - [ {robot_name} ] does not exist. Switch map - [ FAIL ]",
                }
                return response

            response = {"data": {}, "success": False, "msg": ""}
            response["success"] = True
            selected_ib.stop()
            print("Freezing all APIs to simulate a connection loss")
            time.sleep(30)
            print(f"Stop API called")
            return response

        @app.post("/resume", response_model=Response)
        async def resume(robot_name: str):

            response = {}
            selected_ib = self.check_if_robot_exists(robot_name)
            if selected_ib is None:
                response = {
                    "success": False,
                    "msg": f"Error - [ {robot_name} ] does not exist. Switch map - [ FAIL ]",
                }
                return response

            response = {"data": {}, "success": False, "msg": ""}
            response["success"] = True
            selected_ib.resume()
            return response

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="warning",
        )

    def check_if_robot_exists(self, robot_name: str):
        # Determine if requested robot exists
        selected_ib = None
        for ib in self.ib_fleet:
            if ib.name == robot_name:
                selected_ib = ib
                return selected_ib
        return None    


def main():
    parser = argparse.ArgumentParser(
        prog="invisibot", description="Configure and spin up the invisibot"
    )

    parser.add_argument(
        "-p", "--port", type=int, default=8080, help="Port to run the API server on"
    )
    args = parser.parse_args()

    ROBOTS_DATA = None
    with open('robots.json', 'r') as file:
        ROBOTS_DATA = json.load(file)
    
    assert ROBOTS_DATA is not None

    try:
        ApiServer(
            port=args.port,
            robots_data=ROBOTS_DATA
        )

    except Exception as e:

        print(
            f"Error trying to open with error {e}. Try running with the -c or --help flag"
        )
        sys.exit(-1)
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
