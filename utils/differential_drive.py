import copy
import math
import time
from collections import deque
from threading import Condition, Lock, Thread

from utils.messages import Request


class Invisibot:
    """
    Simulates a robot's movement and task execution.
    The robot moves towards a series of target points, managed in a queue.
    """

    def __init__(
        self, x: float = 0.0, y: float = 0.0, yaw: float = 0.0, floor: str = "L1"
    ):
        """
        Initializes the Invisibot with its starting position and other parameters.

        Args:
            x (float): Initial X-coordinate of the robot.
            y (float): Initial Y-coordinate of the robot.
            yaw (float): Initial yaw (orientation) of the robot in radians.
            floor (str): Initial floor level of the robot.
        """
        self.current_x = x
        self.current_y = y
        self.current_yaw = yaw
        self.floor = floor

        self.target_x = x  # Initialize with current position
        self.target_y = y  # Initialize with current position

        self.speed = 0.6  # Default movement speed

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.last_update_time = None
        self.robot_lock = Lock()  # Protects robot's state (position, speed, etc.)

        self.task_queue = deque([])  # Stores upcoming movement tasks (destinations)
        self.task_condition = Condition()  # Used to signal new tasks
        self.current_command_id = (
            0  # ID of the command currently being executed or last completed
        )
        self.current_path_segment = []  # List of points in the current path

        self._is_stopped = False  # Flag to pause/resume robot movement
        self.is_moving = False  # Flag indicating if the robot is actively moving

        self.last_ignored_target = (
            None  # Stores the last target that was ignored due to being a duplicate
        )

        # Start the movement thread as a daemon
        self.movement_thread = Thread(
            target=self._process_movement_tasks,
            daemon=True,
        )
        self.movement_thread.start()

    def _calculate_velocities(self) -> None:
        """
        Calculates the x and y components of the robot's speed
        based on the vector pointing from its current position to the target.
        Also updates the robot's yaw.
        """
        angle_to_target = math.atan2(
            self.target_y - self.current_y, self.target_x - self.current_x
        )
        self.velocity_x = self.speed * math.cos(angle_to_target)
        self.velocity_y = self.speed * math.sin(angle_to_target)
        self.current_yaw = angle_to_target

    def _move_to_point(
        self, target_x: float, target_y: float, target_yaw: float
    ) -> None:
        """
        Simulates the robot moving from its current position to a specified target point.
        This method updates the robot's position over time.

        Args:
            target_x (float): The X-coordinate of the destination.
            target_y (float): The Y-coordinate of the destination.
            target_yaw (float): The desired yaw at the destination.
        """
        with self.robot_lock:
            self.target_x = target_x
            self.target_y = target_y

            print(
                f"####### SETTING TARGET: X={self.target_x:.3f}, Y={self.target_y:.3f}, Yaw={target_yaw:.3f} #######"
            )
            print(
                f"####### ROBOT AT: X={self.current_x:.3f}, Y={self.current_y:.3f}, Yaw={self.current_yaw:.3f} #######"
            )

            original_x = self.current_x
            original_y = self.current_y
            self._calculate_velocities()
            self.last_update_time = time.time()

            # Calculate the time needed to reach the target in X and Y dimensions
            # Handle cases where velocity might be zero to avoid division by zero
            print(f"{self.velocity_x} {self.velocity_y}")
            time_to_target_x = (
                (self.target_x - original_x) / self.velocity_x
                if self.velocity_x != 0
                else 0.0
            )
            time_to_target_y = (
                (self.target_y - original_y) / self.velocity_y
                if self.velocity_y != 0
                else 0.0
            )

            # The total time to reach the point is the maximum of the times for X and Y components
            total_travel_time = max(abs(time_to_target_x), abs(time_to_target_y))

            # If the target is the current position, consider travel time 0
            if math.isclose(self.current_x, target_x) and math.isclose(
                self.current_y, target_y
            ):
                total_travel_time = 0.0

            start_movement_time = time.time()

            while True:
                time_elapsed_since_start = time.time() - start_movement_time

                if time_elapsed_since_start >= total_travel_time:
                    # Snap to target to ensure exact arrival
                    self.current_x = self.target_x
                    self.current_y = self.target_y
                    break  # Reached the target point

                # Update position based on elapsed time and calculated velocities
                self.current_x = original_x + time_elapsed_since_start * self.velocity_x
                self.current_y = original_y + time_elapsed_since_start * self.velocity_y

                print(
                    f"Robot Position @ X: {self.current_x:.3f} Y: {self.current_y:.3f} | "
                    f"Paths Remaining: {len(self.current_path_segment)}"
                )

                # Simulate discrete movement updates
                time.sleep(0.1)

                # Handle stopping functionality
                while self._is_stopped:
                    print("#### ROBOT STOPPED ####")
                    time.sleep(1)  # Wait while stopped

            print(f"Time elapsed for segment: {time_elapsed_since_start:.2f} seconds")

    def _process_movement_tasks(self) -> None:
        """
        Worker thread function that continuously processes movement tasks from the queue.
        It waits for new tasks if the queue is empty.
        """
        while True:
            with self.task_condition:
                while not self.task_queue:
                    self.task_condition.wait()  # Wait until a new task is added

                command_id, target_request = self.task_queue.popleft()

            # Check for duplicate targets to ignore
            last_dest_point = target_request.destination[-1]
            if (
                self.last_ignored_target
                and self.last_ignored_target.x == last_dest_point.x
                and self.last_ignored_target.y == last_dest_point.y
                and self.last_ignored_target.yaw == last_dest_point.yaw
                and self.last_ignored_target.timestamp == last_dest_point.timestamp
            ):
                print(f"Target is a duplicate for command ID {command_id}. Ignoring.")
                self.current_command_id = command_id
                self.current_path_segment = []  # Clear current path
                continue
            else:
                self.last_ignored_target = last_dest_point

            self.current_path_segment = copy.copy(target_request.destination)
            self.is_moving = True

            for point in self.current_path_segment:
                self._move_to_point(point.x, point.y, point.yaw)
                # If needed, update floor as per target_request.map_name
                # self.floor = target_request.map_name # Uncomment if this functionality is desired

            self.current_command_id = command_id
            print(f"Finished command ID: {command_id}")
            self.is_moving = False

    def move(self, cmd_id: int, target_request: Request) -> None:
        """
        Adds a new movement command (a series of destination points) to the task queue.
        The robot will process these commands in a FIFO (First-In, First-Out) manner.

        Args:
            cmd_id (int): A unique identifier for the movement command.
            target_request (Request): An object containing the destination path.
                                     (e.g., target_request.destination is a list of Location objects)
        """
        with self.task_condition:
            self.task_queue.append([cmd_id, target_request])
            self.task_condition.notify()  # Wake up the movement thread if it's waiting

        if self._is_stopped:
            print("Robot was stopped, resuming movement to process new task.")
            self._is_stopped = False

    def stop(self) -> None:
        """
        Halts the robot's current movement. The robot will remain stationary
        until `resume()` is called.
        """
        self._is_stopped = True
        print("Robot received STOP command.")

    def resume(self) -> None:
        """
        Resumes the robot's movement if it was previously stopped.
        """
        if self._is_stopped:
            self._is_stopped = False
            print("Robot received RESUME command.")
        else:
            print("Robot is not currently stopped.")
