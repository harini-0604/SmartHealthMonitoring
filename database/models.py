
from dataclasses import dataclass


@dataclass
class Incident:
    timestamp: str
    source: str
    reason: str
    status: str
