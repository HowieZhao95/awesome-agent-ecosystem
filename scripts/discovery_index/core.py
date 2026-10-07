"""Importable API for composing the legacy index into the public catalog."""
from pathlib import Path

import importlib.util


_SCRIPT = Path(__file__).resolve().parents[1] / "discovery-index.py"
_SPEC = importlib.util.spec_from_file_location("_discovery_index_cli", _SCRIPT)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Cannot load discovery index implementation at {_SCRIPT}")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


def build_index(data_path, resources_path, overrides_path):
    """Build the browse index; categories.yaml is resolved beside the data file."""
    categories_path = Path(data_path).resolve().parents[1] / "categories.yaml"
    return _MODULE.build_index(data_path, resources_path, categories_path, overrides_path)
