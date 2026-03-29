import tempfile
import unittest
import zipfile
from pathlib import Path

from exports.analytical_advisor.__main__ import _archive_export_dir as archive_analytical
from exports.financial_transactions_agent.__main__ import (
    _archive_export_dir as archive_financial,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class ReadmeSmokeTests(unittest.TestCase):
    def test_top_level_readme_uses_repo_relative_links(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertNotIn("/Users/", readme)
        self.assertIn("(agents/analytical_advisor/README.md)", readme)
        self.assertIn("(exports/financial_transactions_agent/README.md)", readme)


class ArchiveSmokeTests(unittest.TestCase):
    def _assert_archive_contains_agent_json(self, archive_path: Path, agent_name: str) -> None:
        self.assertTrue(archive_path.exists(), f"expected archive to exist: {archive_path}")
        self.assertEqual(".zip", archive_path.suffix)

        with zipfile.ZipFile(archive_path) as zipped:
            names = set(zipped.namelist())

        self.assertIn(f"{agent_name}/agent.json", names)

    def test_analytical_archive_helper_creates_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            archive_path = archive_analytical(Path(tempdir))
            self._assert_archive_contains_agent_json(archive_path, "analytical_advisor")

    def test_financial_archive_helper_creates_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            archive_path = archive_financial(Path(tempdir))
            self._assert_archive_contains_agent_json(
                archive_path,
                "financial_transactions_agent",
            )


if __name__ == "__main__":
    unittest.main()
