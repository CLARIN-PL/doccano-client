from __future__ import annotations

from typing import List

from doccano_client.models.dimension import Dimension
from doccano_client.repositories.base import BaseRepository


class DimensionRepository:
    def __init__(self, client: BaseRepository):
        self._client = client

    def list(self, project_id: int) -> List[Dimension]:
        response = self._client.get(f"projects/{project_id}/dimension-detail")
        dimensions = [dimension['id'] for dimension in response.json()]
        return dimensions
    
    def create(self, project_id: int, dimension: Dimension) -> Dimension:
        response = self._client.post(f"projects/{project_id}/assign_dimensions", json={"dimension": dimension})
        for dim in response.json()['dimension']:
            Dimension.parse_obj({"project": project_id, "dimension": dim})
        return response.json()['dimension']
    