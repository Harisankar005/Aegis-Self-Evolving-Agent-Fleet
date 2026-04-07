# Suggested Improvements for Aegis

## High-impact engineering improvements

1. **Package and import hygiene**
   - Add a formal Python package layout (`services/` as installable package) and enforce import stability in CI.
   - Keep `pytest.ini` + optionally editable install (`pip install -e .`) to avoid environment-dependent import failures.

2. **Deterministic evaluation and regression gating**
   - Version and freeze the golden dataset schema.
   - Add strict pass/fail criteria for score drift and agent routing regressions in CI.

3. **Persistent storage upgrades**
   - Move in-memory/session-only stores to pluggable backends (SQLite/Postgres + vector store).
   - Add migration/versioning for long-term memory records.

4. **Safety rails for self-evolving agents**
   - Add capability allowlists, resource budgets, and schema validation for generated agents.
   - Require judge + static checks before runtime registration.

5. **Observability and operations**
   - Emit OpenTelemetry-compatible traces and key mission metrics (success rate, average score, step latency, tool failure rate).
   - Add dashboards and alerting thresholds for quality drops.

## Product and workflow improvements

6. **Mission templates and constraints**
   - Introduce typed mission contracts (goal, audience, budget, channels, compliance constraints) to reduce ambiguity.

7. **Router quality improvements**
   - Combine keyword routing with confidence scoring and fallback policies.
   - Persist per-agent performance feedback and use it in routing decisions.

8. **Tooling reliability**
   - Add retry, timeout, and circuit-breaker policies for HTTP/search tools.
   - Track tool-level SLIs and include tool reliability in judge scoring.

9. **Documentation and onboarding**
   - Add an architecture decision record (ADR) folder for key design choices.
   - Include a “first successful mission in 5 minutes” quickstart with exact commands.

10. **Security hardening**
    - Add prompt-injection filtering for external content.
    - Introduce explicit secret handling guidance and policy checks before deploy steps.

## Quick wins completed in this change

- Added `pytest.ini` so tests can import `services.*` consistently without manual `PYTHONPATH` setup.
