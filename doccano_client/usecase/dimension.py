from __future__ import annotations

from typing import List
from doccano_client.models.dimension import Dimension
from doccano_client.repositories.dimension import DimensionRepository


class DimensionUseCase:
    def __init__(self, repository: DimensionRepository):
        self._repository = repository

    def list(self, project_id: int) -> List[Dimension]:
        return self._repository.list(project_id)

    def create(self, project_id: int, dimension: List) -> Dimension:
        return self._repository.create(project_id, dimension)
