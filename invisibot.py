#!/usr/bin/env python3

import sys
import argparse
from typing import Optional
from pydantic import BaseModel
import logger as lg
from fastapi import FastAPI
import uvicorn

from messages import Request, Response
from differential_drive import Invisibot

# For debug
import traceback
import sys

STANDALONE = False
app = FastAPI()


class ApiServer:
    def __init__(self, robot_name, port, x, y, yaw, floor) -> None:
        self.ib = Invisibot(x, y, yaw, floor)    
        self.robot_name = robot_name
        self.throwaway = None
        
        print("Invisibot ", robot_name, " created at pos ",x ,y, yaw, floor)
        
        @app.post("/path/", response_model=Response)
        async def path(robot_name: str, cmd_id: int, dest: Request):
            response = {
                "success": False,
                "msg": "Beep Boop Beep",
            }
            response["success"] = True
            if self.throwaway is None:
                self.throwaway = dest
            elif self.throwaway.json() == dest.json():
                response["success"] = True
                response["msg"] = "Duplicate requets ignored"
                return response
            
            print("####### Started RMF PATH #######")
            print("####### Cmd id: ", cmd_id," #######")            
            self.ib.move(cmd_id, dest)
            
            for target in dest.destination:
                print(f"Target is [{target.x} {target.y} {target.yaw} {target.timestamp}]")

            return response

        @app.get("/status", response_model=Response)
        async def status():
            response = {"data": {}, "success": False, "msg": ""}
            data = {}
            
            # RMF mainly checks last_completed_request to see what the robot has completed
            data["robot_name"] = self.robot_name
            data["map_name"] = self.ib.floor
            data["position"] = {
                "x": self.ib.self_x,
                "y": self.ib.self_y,
                "yaw": self.ib.self_yaw,
            }
            data["battery"] = 100.0
            data["completed_request"] = False
            data["destination_arrival"] = None
            data["curr_path_size"] = self.ib.curr_path
            data["last_completed_request"] = self.ib.cmd_id
            
            response["data"] = data
            response["success"] = True
            return response

        @app.post("/stop/", response_model=Response)
        async def stop():
            response = {"data": {}, "success": False, "msg": ""}
            response["success"] = True
            self.ib.stop()
            print(f"Stop API called")
            return response

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="warning",
        )

def main():
    logger = lg.init_logger("HIC_MAIN")

    parser = argparse.ArgumentParser(
        prog="invisibot", description="Configure and spin up the invisibot"
    )

    parser.add_argument("-r", "--robot_name", type=str, default="robot1", help="Name of the robot")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Port to run the API server on")
    parser.add_argument(
        "-l", "--location", type=str, default="0.0,0.0,0.0", help="Comma seperated location of the robot (x,y,yaw)"
    )
    parser.add_argument("-m", "--map", type=str, default="L1", help="Current Map of the robot")
    args=parser.parse_args()

    try:
        ApiServer(args.robot_name, args.port, *map(float, args.location.split(",")), args.map).ib.start()

    except Exception as e:
        
        logger.info(
            f"Error trying to open with error {e}. Try running with the -c or --help flag"
        )
        sys.exit(-1)
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
