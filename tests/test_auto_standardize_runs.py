from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
MODULE_PATH = SCRIPTS_DIR / "auto_standardize_runs.py"
sys.path.insert(0, str(SCRIPTS_DIR))
SPEC = importlib.util.spec_from_file_location("auto_standardize_runs", MODULE_PATH)
assert SPEC is not None
auto_standardize_runs = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = auto_standardize_runs
assert SPEC.loader is not None
SPEC.loader.exec_module(auto_standardize_runs)


def write_metrics(run_dir: Path, retention: float = 0.93) -> None:
    run_dir.mkdir(parents=True)
    (run_dir / "metrics.json").write_text(
        json.dumps(
            {
                "project": "Demo Project",
                "experiment": run_dir.name,
                "metrics": {
                    "full_large_f1": 0.8,
                    "route_f1": round(0.8 * retention, 4),
                    "latency_ms": 100,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_auto_standardize_writes_run_records_from_paths_file(tmp_path: Path) -> None:
    runs_root = tmp_path / "project" / "runs"
    run_dir = runs_root / "run-a"
    write_metrics(run_dir, retention=0.9)
    paths_file = tmp_path / "auto_harvest_paths.txt"
    paths_file.write_text(f"# comment\n{runs_root}\n", encoding="utf-8")

    report = auto_standardize_runs.auto_standardize(
        paths=auto_standardize_runs.read_paths_file(paths_file),
        project="Demo Project",
        since_hours=24,
    )

    record_path = run_dir / "run_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert report["written"] == 1
    assert report["failed"] == 0
    assert record["project"] == "Demo Project"
    assert record["status"] == "completed_negative"
    assert record["metrics"]["quality_retention"] == 0.9


def test_auto_standardize_skips_fresh_records(tmp_path: Path) -> None:
    run_dir = tmp_path / "project" / "runs" / "run-a"
    write_metrics(run_dir, retention=1.0)

    first = auto_standardize_runs.auto_standardize(paths=[run_dir], project="Demo Project")
    second = auto_standardize_runs.auto_standardize(paths=[run_dir], project="Demo Project")

    assert first["written"] == 1
    assert second["written"] == 0
    assert second["skipped"] == 1
    assert second["records"][0]["reason"] == "fresh"


def test_auto_standardize_dry_run_does_not_write(tmp_path: Path) -> None:
    run_dir = tmp_path / "project" / "runs" / "run-a"
    write_metrics(run_dir, retention=1.0)

    report = auto_standardize_runs.auto_standardize(paths=[run_dir], project="Demo Project", dry_run=True)

    assert report["written"] == 1
    assert not (run_dir / "run_record.json").exists()


def test_auto_standardize_survives_unreadable_directories(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runs_root = tmp_path / "project" / "runs"
    good_dir = runs_root / "run-good"
    write_metrics(good_dir, retention=1.0)
    blocked_dir = runs_root / "run-blocked"
    blocked_dir.mkdir(parents=True)
    (blocked_dir / "run.metrics.txt").write_text("METRIC accuracy=0.9\n", encoding="utf-8")

    real_iterdir = Path.iterdir

    def guarded_iterdir(self: Path):
        if self.name == blocked_dir.name:
            raise PermissionError(f"simulated unreadable directory: {self}")
        return real_iterdir(self)

    monkeypatch.setattr(Path, "iterdir", guarded_iterdir)

    report = auto_standardize_runs.auto_standardize(paths=[runs_root], project="Demo Project")

    assert report["failed"] == 0
    assert report["written"] == 1
    assert (good_dir / "run_record.json").exists()
    assert not (blocked_dir / "run_record.json").exists()
