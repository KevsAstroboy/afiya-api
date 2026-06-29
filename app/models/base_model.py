from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseModel:
    user: Optional[int]