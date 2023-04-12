from typing import Optional

from pydantic import (
    BaseModel,
)


class Dimension(BaseModel):
    id: Optional[int]
    dimension: int
    project: int
