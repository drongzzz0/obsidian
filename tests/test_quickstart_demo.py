from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"


def load_script_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


init_researchkb_workspace = load_script_module(
    "init_researchkb_workspace_quickstart",
    SCRIPTS_DIR / "init_researchkb_workspace.py",
)
standardize_run = load_script_module("standardize_run_quickstart", SCRIPTS_DIR / "standardize_run.py")
seed_demo_db = load_script_module("seed_demo_db_quickstart", SCRIPTS_DIR / "seed_demo_db.py")


def test_quickstart_demo_loop_includes_standardized_smoke_run(tmp_path: Path) -> None:
    root = tmp_path / "researchkb"
    project_root = tmp_path / "example-project"

    init_result = init_researchkb_workspace.init_workspace(
        root=root,
        project_root=project_root,
        project_name="Smoke Test",
    )
    record = standardize_run.build_run_record(init_result.run_dir)
    record_path = init_result.run_dir / "run_record.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    db_path = seed_demo_db.seed_demo_db(
        root=root,
        examples_dir=REPO_ROOT / "examples",
        force=True,
        include_runs=[record_path],
    )

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """
            select run_id, metrics_json, artifacts_json, decision, next_action, created_at
            from experiment_runs
            where run_id = ?
            """,
            (record["run_id"],),
        ).fetchone()
        latest = conn.execute(
            """
            select run_id
            from experiment_runs
            order by created_at desc
            limit 1
            """
        ).fetchone()
    finally:
        conn.close()

    assert row is not None
    assert latest is not None
    assert latest["run_id"] == "run_smoke_001"
    assert row["run_id"] == "run_smoke_001"
    assert json.loads(row["metrics_json"])
    assert row["decision"]
    assert row["next_action"]
    assert row["created_at"]

    source_locators = json.loads(row["artifacts_json"])
    assert source_locators
    assert "metrics.json" in source_locators
