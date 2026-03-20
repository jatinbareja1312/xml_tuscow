from __future__ import annotations

from django.db import transaction

from CommonUtils.cycle_validation import find_cycles_for_graph
from xml_handler import EdgePayload, GraphPayload, GraphValidationError, NodePayload


class GraphStore:
    """Persistence service that upserts one graph payload atomically."""

    def upsert_graph(self, graph: GraphPayload) -> None:
        """Upsert one graph and replace all related nodes and edges."""
        from django_models.models import Edge, Graph, Node

        with transaction.atomic():
            db_graph = self._upsert_graph_row(GraphModel=Graph, graph=graph)
            node_by_id = self._replace_nodes(
                NodeModel=Node,
                db_graph=db_graph,
                nodes=graph.nodes,
            )
            self._insert_edges(
                EdgeModel=Edge,
                db_graph=db_graph,
                node_by_id=node_by_id,
                edges=graph.edges,
            )
            self._ensure_acyclic(graph_id=db_graph.graph_id)

    def _upsert_graph_row(self, GraphModel, graph: GraphPayload):
        """Create or update the graph row and return persisted graph model."""
        db_graph, _ = GraphModel.objects.update_or_create(
            graph_id=graph.graph_id,
            defaults={"name": graph.name, "is_active": True},
        )
        return db_graph

    def _replace_nodes(self, NodeModel, db_graph, nodes: list[NodePayload]):
        """Delete old nodes and insert new nodes for one graph."""
        NodeModel.objects.filter(graph=db_graph).delete()

        node_by_id = {}
        for node in nodes:
            db_node = NodeModel.objects.create(
                graph=db_graph,
                node_id=node.node_id,
                name=node.name,
                is_active=True,
            )
            node_by_id[node.node_id] = db_node
        return node_by_id

    def _insert_edges(
        self,
        EdgeModel,
        db_graph,
        node_by_id: dict[str, object],
        edges: list[EdgePayload],
    ) -> None:
        """Insert edges using previously inserted node mapping."""
        for edge in edges:
            EdgeModel.objects.create(
                graph=db_graph,
                edge_id=edge.edge_id,
                from_node=node_by_id[edge.from_node],
                to_node=node_by_id[edge.to_node],
                cost=edge.cost,
                is_active=True,
            )

    def _ensure_acyclic(self, graph_id: str) -> None:
        """Raise validation error if one or more cycles are detected."""
        cycles = find_cycles_for_graph(graph_id)
        if cycles:
            raise GraphValidationError(
                f"Incoming graph '{graph_id}' is cyclic. Example cycle: {cycles[0]}"
            )
