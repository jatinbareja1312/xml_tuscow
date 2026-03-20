# EXPLAIN ANALYZE Samples

These samples were captured from PostgreSQL 14 on local seeded graph `g0`.

## 1) `/query` edge-load SQL (used by `API/views/query.py`)

```sql
EXPLAIN ANALYZE
SELECT fn.node_id, tn.node_id, e.cost
FROM edges e
JOIN graphs g ON g.id = e.graph_id
JOIN nodes fn ON fn.id = e.from_node_id
JOIN nodes tn ON tn.id = e.to_node_id
WHERE g.graph_id = 'g0'
ORDER BY e.id;
```

Key plan lines:

```text
Index Scan using graphs_graph_id_bd4541e7_like on graphs g
Bitmap Index Scan on edges_graph_id_87b7cd36
Index Scan using nodes_pkey on nodes fn
Index Scan using nodes_pkey on nodes tn
Execution Time: 0.083 ms
```

## 2) Cycle-detection recursive SQL (`CommonUtils/sql/find_cycles.sql`)

```sql
EXPLAIN ANALYZE
WITH RECURSIVE graph_edges AS (
  ...
)
SELECT ...
```

Key plan lines:

```text
CTE graph_edges
  Index Scan using graphs_graph_id_bd4541e7_like on graphs g
  Bitmap Index Scan on edges_graph_id_87b7cd36
CTE walk
  Recursive Union
  Hash Join
Execution Time: 0.364 ms
```

Notes:
- Small sample graph means costs are tiny; this is expected.
- On larger datasets, `edges(graph_id, from_node_id)` is the critical traversal index.
