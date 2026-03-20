from __future__ import annotations

from pathlib import Path

from django.db import connection


def _sql_file_path() -> Path:
    """Return the absolute path of the shared cycle-detection SQL file."""
    return Path(__file__).resolve().parent / "sql" / "find_cycles.sql"


def _find_cycles_postgres(graph_id: str) -> list[list[str]]:
    """Find cycles for one graph using the shared recursive SQL query."""
    sql = _sql_file_path().read_text(encoding="utf-8")
    with connection.cursor() as cursor:
        # Named parameter binding is used here to prevent SQL injection.
        cursor.execute(sql, {"graph_id": graph_id})
        rows = cursor.fetchall()
    return [row[0] for row in rows if row and row[0]]


def _find_cycles_python(graph_id: str) -> list[list[str]]:
    """Fallback cycle detection for non-Postgres backends."""
    from django_models.models import Edge, Node

    node_ids = list(
        Node.objects.filter(graph__graph_id=graph_id).values_list("node_id", flat=True)
    )
    adjacency = {node_id: [] for node_id in node_ids}
    for from_node, to_node in Edge.objects.filter(graph__graph_id=graph_id).values_list(
        "from_node__node_id", "to_node__node_id"
    ):
        adjacency.setdefault(from_node, []).append(to_node)

    cycles = []
    visited = set()
    stack = []
    in_stack = set()

    def dfs(node: str) -> None:
        visited.add(node)
        stack.append(node)
        in_stack.add(node)

        for next_node in adjacency.get(node, []):
            if next_node not in visited:
                dfs(next_node)
            elif next_node in in_stack:
                start = stack.index(next_node)
                cycles.append(stack[start:] + [next_node])

        stack.pop()
        in_stack.remove(node)

    for node_id in node_ids:
        if node_id not in visited:
            dfs(node_id)

    return cycles


def find_cycles_for_graph(graph_id: str) -> list[list[str]]:
    """Find cycles for a logical graph ID using SQL or a backend-safe fallback."""
    if connection.vendor == "postgresql":
        return _find_cycles_postgres(graph_id)
    return _find_cycles_python(graph_id)
