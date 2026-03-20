from __future__ import annotations

import heapq
from decimal import Decimal


def dfs_paths(
    node_ids: set[str],
    adjacency: dict[str, list[tuple[str, Decimal]]],
    start: str,
    end: str,
) -> list[list[str]]:
    """Return all simple directed paths from start node to end node."""
    if start not in node_ids or end not in node_ids:
        return []

    paths = []

    def dfs(node: str, current_path: list[str], visited: set[str]) -> None:
        if node == end:
            paths.append(current_path.copy())
            return

        for next_node, _ in adjacency.get(node, []):
            if next_node in visited:
                continue

            visited.add(next_node)
            current_path.append(next_node)
            dfs(next_node, current_path, visited)
            current_path.pop()
            visited.remove(next_node)

    dfs(start, [start], {start})
    return paths


def dijkstra_path(
    node_ids: set[str],
    adjacency: dict[str, list[tuple[str, Decimal]]],
    start: str,
    end: str,
) -> list[str] | None:
    """Return lowest-cost path using Dijkstra-style traversal."""
    if start not in node_ids or end not in node_ids:
        return None

    if start == end:
        return [start]

    queue = [(Decimal("0"), (start,), start)]
    best_cost = {start: Decimal("0")}
    best_path = {start: (start,)}

    while queue:
        current_cost, current_path, node = heapq.heappop(queue)

        if current_cost > best_cost[node]:
            continue
        if current_cost == best_cost[node] and current_path > best_path[node]:
            continue

        if node == end:
            return list(current_path)

        for next_node, edge_cost in adjacency.get(node, []):
            new_cost = current_cost + edge_cost
            new_path = current_path + (next_node,)

            old_cost = best_cost.get(next_node)
            old_path = best_path.get(next_node)

            if old_cost is None or new_cost < old_cost:
                best_cost[next_node] = new_cost
                best_path[next_node] = new_path
                heapq.heappush(queue, (new_cost, new_path, next_node))
                continue

            if old_cost == new_cost and (old_path is None or new_path < old_path):
                best_path[next_node] = new_path
                heapq.heappush(queue, (new_cost, new_path, next_node))

    return None
