from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class Car:
    id: int
    frame: int
    time_second: int
    timestamp: str
    type: str
    color: str
    h : int
    s : int
    v : int
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: int
    image: np.ndarray

@dataclass
class Frame:
    frame_id: int
    cars: List[Car]