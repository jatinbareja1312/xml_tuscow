from __future__ import annotations

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from rest_framework.response import Response
from rest_framework.views import APIView

from API.views.query import post as post_query


def _to_response(response: Any) -> Response:
    """Normalize view return values into a DRF Response."""
    if isinstance(response, Response):
        return response
    if isinstance(response, dict) and "status_code" in response and "body" in response:
        return Response(response["body"], status=response["status_code"])
    return Response(response)


def _dispatch(method: str, handlers: dict[str, Callable]) -> Callable | None:
    """Resolve one HTTP method handler from an explicit mapping."""
    return handlers.get(method.lower())


class QueryAPIView(APIView):
    """Single endpoint API view for POST /query."""

    def post(self, request):
        handler = _dispatch(request.method, {"post": post_query})
        if handler is None:
            return Response({"detail": "Method not allowed."}, status=HTTPStatus.METHOD_NOT_ALLOWED)
        return _to_response(handler(request))
