from __future__ import annotations

from CommonUtils.django_setup import bootstrap_django

bootstrap_django(current_file=__file__)

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from API.api_handler import QueryAPIView
from django_models.models import Edge, Graph, Node


class QueryAPIViewTest(TestCase):
    def setUp(self) -> None:
        graph = Graph.objects.create(graph_id="g0", name="Graph", is_active=True)
        a = Node.objects.create(graph=graph, node_id="a", name="A", is_active=True)
        b = Node.objects.create(graph=graph, node_id="b", name="B", is_active=True)
        e = Node.objects.create(graph=graph, node_id="e", name="E", is_active=True)

        Edge.objects.create(
            graph=graph, edge_id=1, from_node=a, to_node=b, cost=10, is_active=True
        )
        Edge.objects.create(
            graph=graph, edge_id=2, from_node=b, to_node=e, cost=20, is_active=True
        )
        Edge.objects.create(
            graph=graph, edge_id=3, from_node=a, to_node=e, cost=5, is_active=True
        )

    def test_query_endpoint_returns_paths_and_cheapest(self) -> None:
        factory = APIRequestFactory()
        request = factory.post(
            "/query",
            {
                "queries": [
                    {"paths": {"start": "a", "end": "e"}},
                    {"cheapest": {"start": "a", "end": "e"}},
                ]
            },
            format="json",
        )

        response = QueryAPIView.as_view()(request)

        assert response.status_code == 200
        assert response.data["answers"][0]["paths"]["paths"] == [["a", "b", "e"], ["a", "e"]]
        assert response.data["answers"][1]["cheapest"]["path"] == ["a", "e"]
