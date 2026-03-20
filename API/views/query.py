from __future__ import annotations

from http import HTTPStatus
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.conf import settings

from CommonUtils.algorithms import dfs_paths as find_all_paths
from CommonUtils.algorithms import dijkstra_path as find_cheapest_path
from django_models.models import Edge, Node


@dataclass(frozen=True)
class GraphData:
    node_ids: set[str]
    adjacency: dict[str, list[tuple[str, Decimal]]]


class QueryPayloadError(ValueError):
    """Raised when /query payload is not valid."""


def post(request) -> dict:
    """Handle POST /query requests."""
    try:
        queries = _normalize_query_payload(request.data)

        graph_data = load_graph_data(settings.APP_GRAPH_ID)
        payload = {"answers": [answer_query(query, graph_data) for query in queries]}
    except Exception as exc:
        return {
            "status_code": HTTPStatus.BAD_REQUEST,
            "body": {"detail": f"Invalid /query payload: {exc}"},
        }
    return {"status_code": HTTPStatus.OK, "body": payload}


def load_graph_data(graph_id: str) -> GraphData:
    """
    Loads graph data from the database for a given graph ID.

    Args:
        graph_id (str): The unique identifier of the graph to load.

    Returns:
        GraphData: An object containing the set of node IDs and adjacency list for the graph.
    """
    node_ids = set(
        Node.objects.filter(graph__graph_id=graph_id).values_list("node_id", flat=True)
    )
    adjacency = {node_id: [] for node_id in node_ids}

    edge_rows = (
        Edge.objects.filter(graph__graph_id=graph_id)
        .order_by("id")
        .values_list("from_node__node_id", "to_node__node_id", "cost")
    )

    for from_node_id, to_node_id, cost in edge_rows:
        adjacency[from_node_id].append((to_node_id, cost))

    return GraphData(node_ids=node_ids, adjacency=adjacency)


def answer_query(query: dict[str, dict[str, str]], graph_data: GraphData) -> dict:
    """Build one answer object for either `paths` or `cheapest` query."""
    query_type, query_data = next(iter(query.items()))
    start, end = query_data["start"], query_data["end"]

    if query_type == "paths":
        paths = find_all_paths(
            node_ids=graph_data.node_ids,
            adjacency=graph_data.adjacency,
            start=start,
            end=end,
        )
        return {"paths": {"from": start, "to": end, "paths": paths if paths else False}}

    path = find_cheapest_path(
        node_ids=graph_data.node_ids,
        adjacency=graph_data.adjacency,
        start=start,
        end=end,
    )
    return {"cheapest": {"from": start, "to": end, "path": path if path is not None else False}}


# -----------------------
# Payload validation helpers
# These functions validate incoming graph query input.
# -----------------------
def _normalize_query_payload(payload: Any) -> list[dict[str, dict[str, str]]]:
    """Validate and normalize POST /query payload."""
    if not isinstance(payload, dict):
        raise QueryPayloadError("request body must be a JSON object.")

    queries = payload.get("queries")
    if not isinstance(queries, list) or not queries:
        raise QueryPayloadError("'queries' must be a non-empty array.")

    return [_normalize_query_item(item, index) for index, item in enumerate(queries)]


def _normalize_query_item(item: Any, index: int) -> dict[str, dict[str, str]]:
    """Normalize one query object and validate required keys."""
    if not isinstance(item, dict) or len(item) != 1:
        raise QueryPayloadError(
            f"queries[{index}] must contain exactly one of 'paths' or 'cheapest'."
        )

    query_type, query_data = next(iter(item.items()))
    if query_type not in {"paths", "cheapest"} or not isinstance(query_data, dict):
        raise QueryPayloadError(
            f"queries[{index}] must contain exactly one of 'paths' or 'cheapest'."
        )

    start = query_data.get("start")
    end = query_data.get("end")
    if not isinstance(start, str) or not start.strip():
        raise QueryPayloadError(f"queries[{index}].{query_type}.start must be a non-empty string.")
    if not isinstance(end, str) or not end.strip():
        raise QueryPayloadError(f"queries[{index}].{query_type}.end must be a non-empty string.")

    return {query_type: {"start": start.strip(), "end": end.strip()}}
