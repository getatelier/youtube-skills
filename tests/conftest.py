"""Pytest configuration."""

import sys
from pathlib import Path

EXECUTION_DIR = Path(__file__).resolve().parent.parent / "skills" / "claude-youtube" / "execution"
sys.path.insert(0, str(EXECUTION_DIR))
