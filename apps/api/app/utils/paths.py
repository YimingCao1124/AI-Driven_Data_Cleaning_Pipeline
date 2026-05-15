"""Path-safety helpers."""
from __future__ import annotations

from pathlib import Path


def is_within(child: Path, parent: Path) -> bool:
    """Return True iff `child` is the same as or inside `parent` (after resolving)."""
    try:
        child.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True
