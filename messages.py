from datetime import datetime
from typing import List, Optional

from pydantic import BaseConfig, BaseModel


class Location(BaseModel):

    timestamp: Optional[float] = (
        None  # float, but will be converted to builtin_interfaces/Time
    )
    x: Optional[float] = None  # float
    y: Optional[float] = None  # float
    yaw: Optional[float] = None  # float

    obey_approach_speed_limit: Optional[bool] = False
    # Speed limit of the lane leading to this waypoint in m/s
    approach_speed_limit: Optional[float] = None

    level_name: Optional[str] = None
    index: Optional[int] = None


class Response(BaseModel):
    """
    Primary data structure for to WebAPI Response. Recieve responses to your requests in this json format.
    """

    data: Optional[dict] = None
    success: bool
    msg: str


class Request(BaseModel):
    """
    Primary data structure for to WebAPI Requests. Send your requests in this json format.

    Parameters:
    map_name (Optional[str] = None) : Requests the map_name of the requested robot
    task (Optional[str]) = None:   Requests the current task of the robot I.e. docking.
    destination: Any = None: Requests the robot to approach a destination.
        Robot will execute the BasicNavigator got goToPose, goThroughPoses, or followWaypoints functions.
        The function selection will be from config "nav2_behaviour" flag.

        goToPose json msg, the Request format is in hospi_api_server/test/goToPose.json
        goThroughPoses and goThroughPoses json msg, the Request is in hospi_api_server/test/gogo.json

    data: Optional[dict] = None #TODO:Implement this
    speed_limit: Optional[float] = None #TODO:Implement this
    toggle: Optional[bool] = None #TODO:Implement this

    i.e.:
        target (Request): A target is in the form described below
            map_name='L1',
            task='1',
            destination=[
                Location(
                    timestamp=1701926411.0,
                    x=45.26679617503545,
                    y=-20.124650184482718,
                    yaw=0.0,
                    obey_approach_speed_limit=False,
                    approach_speed_limit=None,
                    level_name=None,
                    index=21),
                Location(
                    timestamp=...,
                    x=...,
                    ...),
                ...
                Location(...)
                ],
            data=None,
            speed_limit=0.0,
            toggle=True)
    """

    # TODO: Update this to match current use of destination class
    map_name: Optional[str] = None
    task: Optional[str] = None
    destination: List[Location] = None
    data: Optional[str] = None
    speed_limit: Optional[float] = None