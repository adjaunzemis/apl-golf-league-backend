import json
from pathlib import Path


def load_fixture(fixture_path: str):
    """Loads data from JSON file in the 'fixtures' directory at the given subpath."""
    file_path = Path(__file__).parent / "fixtures" / fixture_path
    with file_path.open() as f:
        return json.load(f)
