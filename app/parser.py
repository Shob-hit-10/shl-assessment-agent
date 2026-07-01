import json
from pathlib import Path


class CatalogParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.assessments = []

    def load_catalog(self):
        """Load the SHL catalog JSON file."""

        path = Path(self.file_path)

        if not path.exists():
            raise FileNotFoundError(f"Catalog file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            self.assessments = json.load(f)

        return self.assessments

    def get_all_assessments(self):
        """Return all assessments."""
        return self.assessments