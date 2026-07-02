from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from researchkb_agent_memory import cli  # noqa: E402


def run_cli(capsys: pytest.CaptureFixture[str], *args: str) -> tuple[int, str]:
    code = cli.main(list(args))
    captured = capsys.readouterr()
    return code, captured.out


def test_v040_write_demo_loop_makes_imported_evidence_queryable(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "researchkb"

    code, out = run_cli(capsys, "seed-demo", "--root", str(root), "--examples", str(REPO_ROOT / "examples"))
    assert code == 0
    assert "DEMO_DB_OK" in out

    code, out = run_cli(capsys, "schema-check", "--root", str(root))
    assert code == 0
    assert json.loads(out)["import_ready"] == {
        "import-runs": True,
        "import-bibtex": True,
        "import-notes": True,
        "project-memory": True,
    }

    code, out = run_cli(
        capsys,
        "import-bibtex",
        str(REPO_ROOT / "examples" / "paper-memory" / "demo.bib"),
        "--root",
        str(root),
        "--write",
    )
    assert code == 0
    assert json.loads(out)["inserted"] == 2

    code, out = run_cli(
        capsys,
        "import-notes",
        str(REPO_ROOT / "examples" / "note-memory" / "synthetic-cache-note.md"),
        "--root",
        str(root),
        "--write",
    )
    assert code == 0
    note_import = json.loads(out)
    assert note_import["inserted"] == {"chunks": 1, "claims": 3, "evidence_links": 4}

    code, out = run_cli(capsys, "search-papers", "Synthetic Failure Memory", "--root", str(root))
    assert code == 0
    papers = json.loads(out)["papers"]
    assert any(paper["paper_id"] == "paper_arxiv_2501_00001" for paper in papers)

    code, out = run_cli(capsys, "search-claims", "prompt-template compatibility", "--root", str(root))
    assert code == 0
    claims = json.loads(out)["claims"]
    assert any("prompt-template compatibility" in claim["statement"] for claim in claims)

    code, out = run_cli(capsys, "search-evidence", "incompatible", "--root", str(root))
    assert code == 0
    evidence = json.loads(out)
    assert any(link["source_type"] == "claim" for link in evidence["evidence_links"])
    assert any("incompatible" in link["snippet"] for link in evidence["evidence_links"])
