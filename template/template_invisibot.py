import time
from threading import Condition, Lock, Thread

from differential_drive import Invisibot
from messages import Location, Request


class SomeBiggerSystem:
    def __init__(self):
        x = 10.0
        y = 10.0
        yaw = 0.0
        floor = "L1"
        self.ib = Invisibot(x, y, yaw, floor)

    def move_to(x:float, y:float, yaw:float, floor:str = "L1"):
        
        
    def loop():
        """
        This is a placeholder for the main loop of the system.
        It can be used to continuously check for new requests or perform other tasks.
        """
        while True:
            # Here you would typically check for new requests or perform other operations
            time.sleep(1)
            
if __name__ == '__main__':
    system = SomeBiggerSystem()
    update_thread = Thread(target=system.loop, args=())
    update_thread.start()

    # Move robot to a specific location
    system