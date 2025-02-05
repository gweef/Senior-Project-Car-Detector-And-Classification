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
    confidence: int
    image: str

@dataclass
class Frame:
    frame_id: int
    cars: List[Car]