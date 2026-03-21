from dataclasses import dataclass
from constants import *


@dataclass
class SimulationConfig:
    lanes_per_side: int
    inflow: float
    left_prob: float
    right_prob: float
    traffic_lights: bool
    num_runs: int = NUM_RUNS