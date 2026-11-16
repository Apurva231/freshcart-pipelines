# conftest.py
# Adds the project root to sys.path so that `iris_project` package is importable
# when running pytest from the repo root.
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
