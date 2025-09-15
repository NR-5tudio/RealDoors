import math
import pyray as game
def smooth_oscillation(speed=1.0, range_val=1.0, time=0.0):
    """
    Returns a smooth oscillation value between -range_val and range_val.
    
    Parameters:
    - speed: oscillation speed (1.0 is normal speed)
    - range_val: maximum range of oscillation
    - time: current time value (usually accumulated delta time)
    
    Returns:
    - A value between -range_val and range_val that smoothly oscillates over time
    """
    return math.sin(time * speed) * range_val
class Timer:
    def __init__(self, Once: bool = False) -> None:
        self.time = 0
        self.once = Once
        self.sets = 0
        self.only_once = False

    def Update(self, Seconds: float, delta_time: float = 0):
        delta_time = delta_time - self.sets
        if (delta_time >= Seconds) and self.only_once == False:
            if self.once:
                self.only_once = True
            self.sets += Seconds
            return True
        else:
            return False