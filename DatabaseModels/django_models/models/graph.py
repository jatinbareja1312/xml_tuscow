from __future__ import annotations

from django.db import models

from .base_model import BaseModel


class Graph(BaseModel):
    graph_id = models.CharField(max_length=255, null=False, blank=False, unique=True)
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)

    class Meta:
        db_table = "graphs"
