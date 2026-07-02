# Tool Matrix

Per-surface implementation status for the agent tool contracts in
[agent_tool_contracts.md](agent_tool_contracts.md). "Eval coverage" refers to the gold query
set in [../evals/retrieval_eval.jsonl](../evals/retrieval_eval.jsonl); tools without gold
cases are still covered by unit tests. The engine, `rk-memory` CLI, and MCP server all share
one implementation in `src/researchkb_agent_memory/`.

| Tool | QueryEngine | `rk-memory` CLI | MCP server | Eval coverage | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `search_papers` | yes | `search-papers` | yes | 3 positive + 1 guard | implemented | |
| `search_chunks` | yes | `search-chunks` | yes | 2 positive + 1 guard | implemented | |
| `search_claims` | yes | `search-claims` | yes | 2 positive | implemented | |
| `search_evidence` | yes | `search-evidence` | yes | 1 positive | implemented | Returns evidence links plus matching chunks |
| `find_failure_cases` | yes | `find-failure-cases` | yes | 3 positive + 1 guard | implemented | |
| `find_recent_runs` | yes | `latest-runs` | yes | 2 positive | implemented | Supports project/status filters |
| `compare_runs` | yes | `compare-runs` | yes | unit tests only | implemented | Numeric deltas; non-shared metrics reported in `missing_context` |
| `get_health` | via `health` module | `health` | yes | unit tests only | implemented | Includes `judgement.effectiveness` metrics |
| `find_methods` | no | no | no | none | planned | Compose from `search_claims` + `search_chunks` for now |
| `find_limitations` | no | no | no | none | planned | Compose from `search_claims` + `find_failure_cases` for now |
| `suggest_next_experiment` | no | no | no | none | planned | Compose from `find_recent_runs` + `find_failure_cases` + `search_claims` for now |

The legacy `scripts/query_demo.py` CLI (`papers` / `claims` / `evidence` / `failure-cases` /
`latest-runs` / `compare-runs` subcommands) remains available and delegates to the same engine.

Update this table whenever a tool is added to `researchkb_agent_memory.query`, the
`rk-memory` CLI, the MCP server, or the eval set, and keep it consistent with
`tests/test_rk_mcp_server.py::test_initialize_and_tools_list`.
