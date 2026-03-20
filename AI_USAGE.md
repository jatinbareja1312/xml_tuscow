# AI Usage

AI was used as a coding pair to restructure the project to your requested architecture.

## AI-assisted areas
- Refactoring from the previous layout into Django-centric modules.
- Drafting Django settings, ORM models, and migration runner.
- Drafting and then simplifying API request flow to a single direct `POST /query` handler.
- Drafting the `Jobs/bootstrap_upsert_graph` job entrypoint and parser tests.

## Manual review performed
- Verified the new folder hierarchy matches the requested structure.
- Checked model relationships and constraints.
- Reviewed XML validation rules and DB load flow.
- Verified endpoint shape and query logic for `paths` and `cheapest`.
- Verified unused API serializer module and removed it.

## Final responsibility
All generated code was reviewed and adjusted manually before finalizing.
