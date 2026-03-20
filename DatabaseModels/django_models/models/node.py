from __future__ import annotations

from django.db import models

from .base_model import BaseModel
from .graph import Graph


class Node(BaseModel):
    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, null=False, blank=False)
    node_id = models.CharField(max_length=255, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        db_table = "nodes"
        constraints = [
            models.UniqueConstraint(fields=["graph", "node_id"], name="nodes_graph_nodeid_uq"),
        ]
