"""Root conftest — put the repo root on sys.path so tests import `platform.*`.

The factory plane is imported as the top-level ``platform`` package (locked
taxonomy, section 1.6). Prepending the repo root makes that import resolve when
pytest runs from the repo root.
"""
import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
