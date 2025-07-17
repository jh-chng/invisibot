from typing import List, Optional
from pydantic import BaseModel


class Location(BaseModel):

    timestamp: Optional[float] = (
        None  # float, but will be converted to builtin_interfaces/Time
    )
    x: Optional[float] = None  # float
    y: Optional[float] = None  # float
    yaw: Optional[float] = None  # float
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

    i.e.:
        target (Request): A target is in the form described below
            map_name='L1',
            task='1',
            destination=[
                Location(
                    timestamp=1701926411.0,
                    x=10.0,
                    y=10.0,
                    yaw=0.0,
                    obey_approach_speed_limit=False,
                    approach_speed_limit=None,
                    level_name=None,
                    index=1),
                Location(
                    timestamp=...,
                    x=...,
                    ...),
                ...
                Location(...)
                ],
    """

    map_name: Optional[str] = None
    task: Optional[str] = None
    destination: List[Location] = None
