from decimal import Decimal
from pathlib import Path
import sys

import pytest

job_dir = Path(__file__).resolve().parents[1]
if str(job_dir) not in sys.path:
    sys.path.insert(0, str(job_dir))

from xml_handler import GraphValidationError, parse_graph_xml_string


def test_parse_valid_xml_defaults_cost_to_zero() -> None:
    xml = """
    <graph>
      <id>g1</id>
      <name>Graph</name>
      <nodes>
        <node><id>a</id><name>A</name></node>
        <node><id>b</id><name>B</name></node>
      </nodes>
      <edges>
        <edge><id>e1</id><from>a</from><to>b</to></edge>
      </edges>
    </graph>
    """

    graph = parse_graph_xml_string(xml)

    assert graph.graph_id == "g1"
    assert graph.edges[0].edge_id == 1
    assert graph.edges[0].cost == Decimal("0")


def test_reject_duplicate_node_id() -> None:
    xml = """
    <graph>
      <id>g1</id>
      <name>Graph</name>
      <nodes>
        <node><id>a</id><name>A</name></node>
        <node><id>a</id><name>A2</name></node>
      </nodes>
      <edges />
    </graph>
    """

    with pytest.raises(GraphValidationError, match="Duplicate node id"):
        parse_graph_xml_string(xml)


def test_reject_unknown_edge_target() -> None:
    xml = """
    <graph>
      <id>g1</id>
      <name>Graph</name>
      <nodes>
        <node><id>a</id><name>A</name></node>
      </nodes>
      <edges>
        <edge><id>e1</id><from>a</from><to>b</to></edge>
      </edges>
    </graph>
    """

    with pytest.raises(GraphValidationError, match="unknown <to> node"):
        parse_graph_xml_string(xml)
