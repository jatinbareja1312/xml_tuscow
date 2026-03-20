from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from defusedxml import ElementTree

EDGE_ID_PATTERN = re.compile(r"e(\d+)", flags=re.IGNORECASE)


class GraphValidationError(ValueError):
    """Raised when XML graph content violates constraints."""


@dataclass(frozen=True)
class NodePayload:
    """Validated node payload extracted from XML."""

    node_id: str
    name: str


@dataclass(frozen=True)
class EdgePayload:
    """Validated edge payload extracted from XML."""

    edge_id: int
    from_node: str
    to_node: str
    cost: Decimal


@dataclass(frozen=True)
class GraphPayload:
    """Validated graph payload extracted from XML."""

    graph_id: str
    name: str
    nodes: list[NodePayload]
    edges: list[EdgePayload]


def parse_graph_xml_file(path: str | Path) -> GraphPayload:
    """Parse and validate a graph XML file into a typed payload."""
    return _parse_xml(path, lambda value: ElementTree.parse(value).getroot())


def parse_graph_xml_string(xml_content: str) -> GraphPayload:
    """Parse and validate graph XML content from an in-memory string."""
    return _parse_xml(xml_content, ElementTree.fromstring)


def _parse_xml(source: str | Path, parser: Callable[[str | Path], ElementTree.Element]) -> GraphPayload:
    """Parse XML source and convert syntax errors to GraphValidationError."""
    try:
        root = parser(source)
    except ElementTree.ParseError as exc:
        raise GraphValidationError(f"Invalid XML syntax: {exc}") from exc

    return _parse_graph_root(root)


def _parse_graph_root(root: ElementTree.Element) -> GraphPayload:
    """Validate top-level graph structure and parse nodes/edges."""
    if root.tag != "graph":
        raise GraphValidationError("Root element must be <graph>")

    graph_values = _require_child_text_fields(root, ("id", "name"), "<graph>")
    nodes_group = _require_single_child(root, "nodes", "<graph>")
    edges_group = _optional_single_child(root, "edges", "<graph>")

    if edges_group is not None and list(root).index(edges_group) < list(root).index(nodes_group):
        raise GraphValidationError("<nodes> must appear before <edges>")

    nodes, node_ids = _parse_nodes(nodes_group)
    edges = _parse_edges(edges_group, node_ids)

    return GraphPayload(
        graph_id=graph_values["id"],
        name=graph_values["name"],
        nodes=nodes,
        edges=edges,
    )


def _parse_nodes(nodes_group: ElementTree.Element) -> tuple[list[NodePayload], set[str]]:
    """Parse <nodes> and ensure node IDs are unique and non-empty."""
    node_elements = [child for child in list(nodes_group) if child.tag == "node"]
    if not node_elements:
        raise GraphValidationError("<nodes> must contain at least one <node>")

    nodes: list[NodePayload] = []
    node_ids: set[str] = set()

    for node_element in node_elements:
        node_values = _require_child_text_fields(node_element, ("id", "name"), "<node>")
        node_id = node_values["id"]
        if node_id in node_ids:
            raise GraphValidationError(f"Duplicate node id '{node_id}' is not allowed")

        nodes.append(NodePayload(node_id=node_id, name=node_values["name"]))
        node_ids.add(node_id)

    return nodes, node_ids


def _parse_edges(edges_group: ElementTree.Element | None, node_ids: set[str]) -> list[EdgePayload]:
    """Parse <edges>, validate references, and normalize edge payloads."""
    if edges_group is None:
        return []

    edge_elements = [child for child in list(edges_group) if child.tag in {"edge", "node"}]
    if not edge_elements:
        return []

    seen_edge_ids: set[int] = set()
    return [
        _parse_single_edge(edge_element=edge_element, node_ids=node_ids, seen_edge_ids=seen_edge_ids)
        for edge_element in edge_elements
    ]


def _parse_single_edge(
    edge_element: ElementTree.Element,
    node_ids: set[str],
    seen_edge_ids: set[int],
) -> EdgePayload:
    """Parse one edge, validate endpoints, and return normalized payload."""
    edge_values = _require_child_text_fields(edge_element, ("id", "from", "to"), "<edge>")
    edge_id = _parse_edge_id(edge_values["id"])

    if edge_id in seen_edge_ids:
        raise GraphValidationError(f"Duplicate edge id '{edge_id}' is not allowed")
    seen_edge_ids.add(edge_id)

    from_node = edge_values["from"]
    to_node = edge_values["to"]
    _validate_endpoint(node_ids=node_ids, node_id=from_node, direction="from", edge_id=edge_id)
    _validate_endpoint(node_ids=node_ids, node_id=to_node, direction="to", edge_id=edge_id)

    return EdgePayload(
        edge_id=edge_id,
        from_node=from_node,
        to_node=to_node,
        cost=_parse_optional_non_negative_cost(edge_element),
    )


def _validate_endpoint(node_ids: set[str], node_id: str, direction: str, edge_id: int) -> None:
    """Ensure one edge endpoint references an existing node."""
    if node_id not in node_ids:
        raise GraphValidationError(
            f"Edge '{edge_id}' references unknown <{direction}> node '{node_id}'"
        )


def _parse_edge_id(raw_edge_id: str) -> int:
    """
    Accepts edge IDs as either:
    - prefixed form: e1, e42
    - numeric form: 1, 42
    Stores normalized integer form in DB.
    """
    prefixed_match = EDGE_ID_PATTERN.fullmatch(raw_edge_id)
    if prefixed_match:
        return int(prefixed_match.group(1))

    if raw_edge_id.isdigit():
        return int(raw_edge_id)

    raise GraphValidationError(
        f"Invalid edge id '{raw_edge_id}'. Expected 'e<integer>' or '<integer>'."
    )


def _parse_optional_non_negative_cost(edge_element: ElementTree.Element) -> Decimal:
    """Parse optional edge cost and enforce non-negative decimal values."""
    cost_element = _optional_single_child(edge_element, "cost", "<edge>")
    if cost_element is None:
        return Decimal("0")

    raw_cost = _normalized_text(cost_element, "<cost>")
    try:
        cost = Decimal(raw_cost)
    except InvalidOperation as exc:
        raise GraphValidationError(f"Invalid floating-point <cost> value '{raw_cost}'") from exc

    if cost < 0:
        raise GraphValidationError("<cost> must be non-negative")
    return cost


def _require_child_text_fields(
    parent: ElementTree.Element,
    field_names: tuple[str, ...],
    parent_context: str,
) -> dict[str, str]:
    """Return required child text fields for the requested tags."""
    return {
        field_name: _normalized_text(
            _require_single_child(parent, field_name, parent_context),
            f"<{field_name}>",
        )
        for field_name in field_names
    }


def _require_single_child(
    parent: ElementTree.Element, tag: str, parent_context: str
) -> ElementTree.Element:
    """Return exactly one child element by tag or raise a validation error."""
    matches = [child for child in list(parent) if child.tag == tag]
    if len(matches) != 1:
        raise GraphValidationError(
            f"{parent_context} must contain exactly one <{tag}> element"
        )
    return matches[0]


def _optional_single_child(
    parent: ElementTree.Element, tag: str, parent_context: str
) -> ElementTree.Element | None:
    """Return zero-or-one child element by tag; error if multiple exist."""
    matches = [child for child in list(parent) if child.tag == tag]
    if len(matches) > 1:
        raise GraphValidationError(
            f"{parent_context} can contain at most one <{tag}> element"
        )
    return matches[0] if matches else None


def _normalized_text(element: ElementTree.Element, element_label: str) -> str:
    """Return stripped text content and reject empty values."""
    value = (element.text or "").strip()
    if not value:
        raise GraphValidationError(f"{element_label} cannot be empty")
    return value
