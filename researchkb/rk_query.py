"""Compatibility wrapper. The implementation lives in researchkb_agent_memory.query."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parents[1] / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from researchkb_agent_memory.query import *  # noqa: E402,F403
