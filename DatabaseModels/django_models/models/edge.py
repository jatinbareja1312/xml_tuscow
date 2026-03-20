from __future__ import annotations

from decimal import Decimal

from django.db import models

from .base_model import BaseModel
from .graph import Graph
from .node import Node


class Edge(BaseModel):
    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, related_name="edges", null=False, blank=False)
    edge_id = models.IntegerField(null=False, blank=False)
    from_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="outgoing_edges", null=False, blank=False)
    to_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="incoming_edges", null=False, blank=False)
    cost = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=False, blank=False)

    class Meta:
        db_table = "edges"
        constraints = [
            models.UniqueConstraint(fields=["graph", "edge_id"], name="edges_graph_edgeid_uq"),
            models.CheckConstraint(check=models.Q(cost__gte=0), name="edge_cost_gte_zero"),
        ]
        indexes = [
            models.Index(fields=["graph", "from_node"], name="idx_edges_graph_from"),
            models.Index(fields=["graph", "id"], name="idx_edges_graph_id"),
        ]
