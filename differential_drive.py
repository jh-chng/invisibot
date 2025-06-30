import math
import time
import copy
from threading import Thread, Lock, Condition
from collections import deque  # For storing tasks
from messages import Request

class Invisibot:
    def __init__(self, x: float = 45.26, y: float = -20.124, yaw: float = 0.0, floor: str = "L1"):
        self.target_x = -10.0
        self.target_y = 10.0

        self.speed_in_x = None
        self.speed_in_y = None

        self.speed = 0.6

        self.self_x = x
        self.self_y = y
        self.self_yaw = yaw
        self.floor = floor

        self.start_time = None
        self.lock = Lock()

        # For storing paths
        self.dest_stack = deque([])
        self.waitfordest = Condition()
        self.cmd_id = 0
        self.curr_path = []
        
        self._stop = False
        
        # For connectivity flags
        # self.servermode = ServerMode.server
        
        # For ignoring paths
        self.ignore_target = False

        t = Thread(
            target=self.moving,
            daemon=True,
        )
        t.start()

    """
    Break the vector between robot and target into X and Y components
    The x is then self.speed_in_x, and y is self.speed_in_y
    """
    def rotate_speed_vector(self):
        self.speed_in_x = self.speed * math.cos(
            math.atan2(self.target_y - self.self_y, self.target_x - self.self_x)
        )
        self.speed_in_y = self.speed * math.sin(
            math.atan2(self.target_y - self.self_y, self.target_x - self.self_x)
        )
        self.self_yaw = math.atan2(
            self.target_y - self.self_y, self.target_x - self.self_x
        )

    def go_to_point(self, target_x: float, target_y: float, target_yaw: float):
        elasped_time = 0.0
        with self.lock:
            # pdb.set_trace()
            self.target_x = target_x
            self.target_y = target_y
            print(
                "######### SET TARGET #########", self.target_x, self.target_y, target_yaw
            )

            print("######### ROBOT AT ######### ", self.self_x, self.self_y, self.self_yaw)

            # Init
            orig_x = self.self_x
            orig_y = self.self_y
            self.rotate_speed_vector()
            self.start_time = time.time()

            # print("Orig ", orig_x, orig_y)
            # print("speed ", self.speed_in_x, self.speed_in_y)
            x_time_taken = 0.0
            y_time_taken = 0.0

            if (self.speed_in_x ==0):
                x_time_taken = 0.0
            else:
                x_time_taken = (self.target_x - self.self_x) / self.speed_in_x
                
            if self.speed_in_y ==0:
                y_time_taken = 0.0
            else:
                y_time_taken = (self.target_y - self.self_y) / self.speed_in_y
            
            while True:
                time_now = time.time()
                
                # Update position of robot
                elasped_time = time_now - self.start_time

                if x_time_taken == 0.0:
                    self.self_x = orig_x
                if y_time_taken == 0.0:
                    self.self_y = orig_y
                    
                if (time_now > self.start_time + x_time_taken) and (
                    time_now > self.start_time + y_time_taken
                ):
                    # self.curr_path.pop(0)
                    break

                self.self_x = orig_x + elasped_time * self.speed_in_x
                self.self_y = orig_y + elasped_time * self.speed_in_y
                time.sleep(0.1)

                print(f"Robot is at {self.self_x}, {self.self_y}, {len(self.curr_path)}")

                if len(self.curr_path) >1:
                    first = [self.curr_path[0].x,
                                self.curr_path[0].y]
                    second = [self.curr_path[1].x,
                                self.curr_path[1].y]
                    robot = [self.self_x, self.self_y]
                        
                    # if  line_follwing(robot, robot, first, 0.1):
                    #     if len(self.curr_path) == 1:
                    #         self.curr_path = None    
                    #     self.curr_path.pop(0)        
                                
                if self._stop:
                    print("####STOPPED####")
                    return
                
        print("elasped_time ", elasped_time)

    def moving(
        self,
    ):
        while True:
            # If there is no workload, wait.
            self.waitfordest.acquire()
            while len(self.dest_stack) == 0:
                self.waitfordest.wait()

            # pop off workload and do work
            [cmd_id, targets] = self.dest_stack.popleft()
            self.waitfordest.release()
            
            if self._stop:
                self.dest_stack.clear()
                return
            
            # RMF will send the same targets for some reason. Ignore.            
            if self.ignore_target:
                if self.ignore_target.x == targets.destination[-1].x and \
                    self.ignore_target.y == targets.destination[-1].y and \
                    self.ignore_target.yaw == targets.destination[-1].yaw and \
                    self.ignore_target.timestamp == targets.destination[-1].timestamp:
                    print("Target is the same. Ignoring")
                    print("Done with ", cmd_id)
                    self.cmd_id = cmd_id
                    self.curr_path = None
                    continue
                else:
                    self.ignore_target = targets.destination[-1]   
            else:
                self.ignore_target = targets.destination[-1]
            
            # Unwrap target of type Request into it's components
            self.curr_path = copy.copy(targets.destination)
            for target in targets.destination:
                self.go_to_point(target.x, target.y, target.yaw)
                self.floor = targets.map_name
            self.cmd_id = cmd_id
            print("Done with ", cmd_id)
                
    def move(self, cmd_id: int, target: Request):
        """Pushes the next target onto the queue, FIFO. The bot pops off the
        target and cmd_id and executes it. self.cmd_id is updated when done.

        Args:
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
                        ...)
                    ],
                data=None,
                speed_limit=0.0,
                toggle=True)
        """
        self.waitfordest.acquire()
        self.dest_stack.append([cmd_id, target])
        self.waitfordest.notify()
        self.waitfordest.release()
        if self._stop:
            self._stop = False

    def stop(self,):
        self._stop = True