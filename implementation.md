# Implementation Notes

This document explains the implementation choices in this repository, the reasoning behind each choice, trade-offs, and better alternatives for each major step.

## 1. Overall Architecture

### Implemented choice
- Split into 3 major areas:
- `Jobs/bootstrap_upsert_graph`: XML parsing + validation + persistence.
- `DatabaseModels`: Django model layer + migrations.
- `API`: REST query endpoint (`POST /query`).

### Why
- Keeps ingestion concerns separate from read/query concerns.
- Makes local testing and debugging easier.

### Trade-offs
- Some setup/bootstrap code is repeated across entry points.
- Multiple folders can increase navigation overhead for a small challenge.

### Better alternatives
1. Use a single Django project with Django management commands for ingestion (`manage.py import_graph ...`) to reduce bootstrapping duplication.
2. Use a service layer package (for example `Domain/graph_service.py`) shared by both API and job.

## 2. XML Parsing Library

### Implemented choice
- `defusedxml.ElementTree` is used in `Jobs/bootstrap_upsert_graph/xml_handler.py`.

### Why
- Safer XML parsing than standard `xml.etree` defaults for untrusted input.
- Familiar API and low complexity.

### Trade-offs
- DOM-style parse reads full tree in memory.

### Better alternatives
1. Use streaming parse (`iterparse`) for very large XML inputs.
2. Use schema validation (XSD) if strict XML contract validation is required.

## 3. XML Validation Rules

### Implemented choice
- Semantic checks implemented directly in parser flow:
- graph `id` + `name` required.
- `<nodes>` before `<edges>`.
- at least one node.
- unique node IDs.
- edge endpoints must exist.
- optional non-negative `cost`, default `0`.

### Why
- Closely matches challenge rules with readable, direct checks.

### Trade-offs
- Validation is imperative and spread across helper methods.

### Better alternatives
1. Introduce a dedicated validation layer with typed error codes (instead of only messages).
2. Add property-based tests for validation edge cases.

## 4. Persistence / Upsert Strategy

### Implemented choice
- `GraphStore.upsert_graph()` uses `update_or_create()` on graph and recreates nodes/edges in a transaction.

### Why
- Easy to reason about and idempotent for repeated imports.

### Trade-offs
- Deletes/reinserts can be expensive for large graphs.
- Loses stable PK identity for nodes/edges across reloads.

### Better alternatives
1. Diff-based upsert for nodes/edges to minimize churn.
2. Bulk operations (`bulk_create`, `bulk_update`) for performance.

## 5. Data Model / Schema

### Implemented choice
- Normalized model split into `Graph`, `Node`, `Edge` with foreign keys and constraints.
- Common fields in `BaseModel` (`is_active`, `last_updated`).

### Why
- Matches directed graph relational modeling.
- Enforces integrity with FK + uniqueness + non-negative cost constraint.

### Trade-offs
- `name` on `Graph` is unique, which may be stricter than needed.
- Soft-delete field exists but is not yet used by query filters.

### Better alternatives
1. Add explicit partial indexes or filtered queries for `is_active=True`.
2. Add DB-level comments/docs for schema semantics.

## 6. Migration Strategy

### Implemented choice
- Single auto-generated Django migration (`0001_initial.py`).

### Why
- Simple and clean migration history for submission.

### Trade-offs
- Python migration file, not a standalone SQL migration script.

### Better alternatives
1. Add generated SQL migration artifact (for example `DatabaseModels/sql/schema.sql`) to satisfy strict “SQL migration” expectations.
2. Add migration check in CI.

## 7. Cycle Detection Requirement

### Implemented choice
- Added recursive SQL query in `CommonUtils/sql/find_cycles.sql`.

### Why
- Meets requirement #4 as a standalone SQL deliverable.

### Trade-offs
- Not integrated into runtime API/job.
- Potential duplicate cycle rotations in output depending on graph shape.

### Better alternatives
1. Wrap in a SQL function returning canonicalized cycles.
2. Add a test fixture and expected output validation for this query.

## 8. API Entry and Routing Pattern

### Implemented choice
- `API/api_handler.py` exposes one straightforward DRF flow for `POST /query`.
- `QueryAPIView.post()` directly calls `post_query()` and returns the response payload.

### Why
- Keeps request handling easy to read and easy to debug for a single-endpoint challenge.

### Trade-offs
- Less extensible than a multi-module dynamic dispatch pattern if many endpoints are added later.

### Better alternatives
1. Keep this direct style until at least 3-5 endpoints exist.
2. If endpoint count grows, move to explicit URL/view registration per endpoint (still no runtime `importlib`).

## 9. API Request Validation and Query Execution

### Implemented choice
- Validation and query-answer assembly are in `API/views/query.py` (`_normalize_query_payload`, `answer_query`).
- `api_handler.py` maps validation errors to HTTP 400.

### Why
- Keeps API handler thin and isolates graph query behavior in one module.

### Trade-offs
- `query.py` now mixes payload validation with graph algorithms.

### Better alternatives
1. Split into `graph_request_validation.py` and `graph_algorithms.py` for cleaner separation.
2. Reintroduce DRF serializers if standardized field-level error payloads are desired.

## 10. Path-Finding Algorithms

### Implemented choice
- All paths: DFS with visited set.
- Cheapest path: Dijkstra-like priority queue over adjacency list.

### Why
- Correct and straightforward for weighted directed graph queries.

### Trade-offs
- `find_all_paths` can explode combinatorially on dense/cyclic graphs.
- No pagination/limits for very large result sets.

### Better alternatives
1. Add max path count / max depth guardrails.
2. Return streaming/chunked results for large path sets.

## 11. Shared Utilities

### Implemented choice
- Created `CommonUtils/django_setup.py` to centralize Django bootstrap (`setup_django`).

### Why
- Removes repeated setup snippets and keeps startup consistent.

### Trade-offs
- Adds one more package to understand for simple scripts.

### Better alternatives
1. Use a single canonical project entrypoint and invoke subcommands from there.
2. Move bootstrap helper into a `scripts/` folder if intended only for tooling.

## 12. Testing Strategy

### Implemented choice
- Unit tests for parser validation (`Jobs/bootstrap_upsert_graph/tests/test_upsert_graph.py`).
- API endpoint behavior test (`API/tests/test_query.py`).
- Simple runner scripts for each area.

### Why
- Covers core challenge functionality and regression checks.

### Trade-offs
- Missing tests for cycle SQL query.
- Minimal negative API payload tests after validation refactor.

### Better alternatives
1. Add dedicated tests for invalid API payloads and no-path cases.
2. Add DB integration test executing `find_cycles.sql` on fixture data.

## 13. Dependencies

### Implemented choice
- Django + DRF + PostgreSQL driver + defusedxml + pytest.
- Requirements split by component.

### Why
- Familiar backend stack and quick local setup.

### Trade-offs
- Component-specific requirement files still exist, so contributors need to know where each dependency belongs.

### Better alternatives
1. Keep `requirements_dev.txt` as the single pinned base and use component files only as thin overlays.
2. Add `pip check` and import-lint in CI.

## 14. Delivery Readiness

### What is currently strong
- Functional XML ingest pipeline.
- Functional `/query` endpoint for `paths` and `cheapest`.
- Recursive SQL cycle query provided.
- Local test runners and CI scaffold present.

### Recommended final polish before submission
1. Update `README.md` with explicit algorithm explanations and library choices (XML + JSON handling).
2. Add a short section showing how to run `find_cycles.sql` with an example parameter.
3. Optionally consolidate requirements into base + overlays (`dev`, `ci`) to reduce drift.
