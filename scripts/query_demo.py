from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path(".runtime") / "researchkb"


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the synthetic ResearchKB demo database.")
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="ResearchKB root. Defaults to .runtime/researchkb.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    latest = subparsers.add_parser("latest-runs", help="Show latest experiment runs.")
    latest.add_argument("--limit", type=int, default=5)

    failures = subparsers.add_parser("failure-cases", help="Search synthetic failure cases.")
    failures.add_argument("query")
    failures.add_argument("--limit", type=int, default=10)

    evidence = subparsers.add_parser("evidence", help="Search synthetic evidence links and chunks.")
    evidence.add_argument("query")
    evidence.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    db_path = args.root / "db" / "literature.sqlite"
    if not db_path.exists():
        raise FileNotFoundError(f"Demo DB not found: {db_path}. Run scripts/seed_demo_db.py first.")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        if args.command == "latest-runs":
            result = latest_runs(conn, args.limit)
        elif args.command == "failure-cases":
            result = failure_cases(conn, args.query, args.limit)
        elif args.command == "evidence":
            result = evidence_search(conn, args.query, args.limit)
        else:
            raise ValueError(f"Unknown command: {args.command}")
    finally:
        conn.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def latest_runs(conn: sqlite3.Connection, limit: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        select run_id, project, experiment, status, dataset, model, seed, config_ref,
               metrics_json, decision, next_action, created_at
        from experiment_runs
        order by created_at desc
        limit ?
        """,
        (limit,),
    ).fetchall()
    return [row_to_dict(row, json_fields={"metrics_json"}) for row in rows]


def failure_cases(conn: sqlite3.Connection, query: str, limit: int) -> list[dict[str, Any]]:
    like = f"%{query.lower()}%"
    rows = conn.execute(
        """
        select problem_id, symptom, context_json, suspected_causes_json, tried_fixes_json,
               final_solution, linked_runs_json, linked_papers_json, confidence
        from problem_cases
        where lower(symptom) like ?
           or lower(final_solution) like ?
           or lower(context_json) like ?
        limit ?
        """,
        (like, like, like, limit),
    ).fetchall()
    return [
        row_to_dict(
            row,
            json_fields={
                "context_json",
                "suspected_causes_json",
                "tried_fixes_json",
                "linked_runs_json",
                "linked_papers_json",
            },
        )
        for row in rows
    ]


def evidence_search(conn: sqlite3.Connection, query: str, limit: int) -> dict[str, list[dict[str, Any]]]:
    like = f"%{query.lower()}%"
    evidence_rows = conn.execute(
        """
        select evidence_id, source_type, source_id, paper_id, chunk_id, locator, quote_or_snippet, confidence
        from evidence_links
        where lower(coalesce(locator, '')) like ?
           or lower(coalesce(quote_or_snippet, '')) like ?
        limit ?
        """,
        (like, like, limit),
    ).fetchall()
    chunk_rows = conn.execute(
        """
        select chunk_id, paper_id, source_type, section, locator, text
        from chunks
        where lower(text) like ?
           or lower(coalesce(section, '')) like ?
           or lower(coalesce(locator, '')) like ?
        limit ?
        """,
        (like, like, like, limit),
    ).fetchall()
    return {
        "evidence_links": [row_to_dict(row) for row in evidence_rows],
        "chunks": [row_to_dict(row) for row in chunk_rows],
    }


def row_to_dict(row: sqlite3.Row, json_fields: set[str] | None = None) -> dict[str, Any]:
    json_fields = json_fields or set()
    payload = dict(row)
    for field in json_fields:
        if payload.get(field):
            payload[field] = json.loads(payload[field])
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
