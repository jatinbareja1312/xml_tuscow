-- Find cycles for one logical graph key (graphs.graph_id).
-- Use $1 as the graph key parameter (example: 'g0').

WITH RECURSIVE graph_edges AS (
    SELECT
        e.graph_id,
        e.from_node_id,
        e.to_node_id
    FROM edges e
    JOIN graphs g ON g.id = e.graph_id
    WHERE g.graph_id = $1
),
walk AS (
    SELECT
        ge.graph_id,
        ge.from_node_id AS start_node_pk,
        ge.to_node_id AS current_node_pk,
        ARRAY[ge.from_node_id, ge.to_node_id] AS node_path
    FROM graph_edges ge

    UNION ALL

    SELECT
        w.graph_id,
        w.start_node_pk,
        ge.to_node_id AS current_node_pk,
        w.node_path || ge.to_node_id
    FROM walk w
    JOIN graph_edges ge
      ON ge.graph_id = w.graph_id
     AND ge.from_node_id = w.current_node_pk
    WHERE cardinality(w.node_path) < 100
      AND (
            ge.to_node_id = w.start_node_pk
            OR NOT ge.to_node_id = ANY(w.node_path)
          )
),
cycles AS (
    SELECT DISTINCT (w.node_path || w.start_node_pk) AS cycle_node_pks
    FROM walk w
    WHERE w.current_node_pk = w.start_node_pk
)
SELECT
    (
        SELECT array_agg(n.node_id ORDER BY u.ord)
        FROM unnest(c.cycle_node_pks) WITH ORDINALITY AS u(node_pk, ord)
        JOIN nodes n ON n.id = u.node_pk
    ) AS cycle_node_ids
FROM cycles c
ORDER BY cycle_node_ids;
