-- Normalized PostgreSQL schema for directed graphs.
-- Mirrors the Django models used by this repository.

CREATE TABLE IF NOT EXISTS graphs (
    id BIGSERIAL PRIMARY KEY,
    graph_id VARCHAR(255) NOT NULL UNIQUE, -- logical graph key from XML (<graph><id>)
    name VARCHAR(255) NOT NULL UNIQUE,     -- graph display name (<graph><name>)
    is_active BOOLEAN NOT NULL,            -- shared lifecycle flag
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS nodes (
    id BIGSERIAL PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graphs (id) ON DELETE CASCADE, -- parent graph
    node_id VARCHAR(255) NOT NULL,                                    -- logical node key from XML
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT nodes_graph_nodeid_uq UNIQUE (graph_id, node_id)       -- node keys unique inside one graph
);

CREATE TABLE IF NOT EXISTS edges (
    id BIGSERIAL PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graphs (id) ON DELETE CASCADE, -- parent graph
    edge_id INTEGER NOT NULL,                                          -- normalized integer edge key
    from_node_id BIGINT NOT NULL REFERENCES nodes (id) ON DELETE CASCADE,
    to_node_id BIGINT NOT NULL REFERENCES nodes (id) ON DELETE CASCADE,
    cost NUMERIC(20, 2) NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT edges_graph_edgeid_uq UNIQUE (graph_id, edge_id),
    CONSTRAINT edge_cost_gte_zero CHECK (cost >= 0)
);

-- Traversal/read indexes
CREATE INDEX IF NOT EXISTS idx_edges_graph_from ON edges (graph_id, from_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_graph_id ON edges (graph_id, id);
