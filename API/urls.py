from __future__ import annotations

from django.urls import path

from API.api_handler import QueryAPIView

urlpatterns = [
    path("query", QueryAPIView.as_view(), name="query"),
]
