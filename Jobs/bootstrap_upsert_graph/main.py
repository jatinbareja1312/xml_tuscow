from __future__ import annotations

from pathlib import Path

from CommonUtils.django_setup import bootstrap_django
from graph_store import GraphStore
from xml_handler import parse_graph_xml_file

SAMPLE_XML_FILE = Path(__file__).with_name("sample_graph.xml")


def main() -> None:
    """CLI entrypoint that imports the bundled sample graph XML."""
    bootstrap_django(current_file=__file__)
    graph = parse_graph_xml_file(SAMPLE_XML_FILE)
    GraphStore().upsert_graph(graph)
    print(
        f"Loaded graph '{graph.graph_id}' with {len(graph.nodes)} node(s) "
        f"and {len(graph.edges)} edge(s)."
    )


if __name__ == "__main__":
    main()
