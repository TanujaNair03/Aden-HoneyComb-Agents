"""Helper script to validate, demo, and archive the Hive Analytical Advisor agent."""

import argparse
import asyncio
import json
import shutil
import sys
from pathlib import Path


def _bootstrap_paths() -> Path:
    """
    Add local Hive-style import roots.

    This lets the helper work when run from a project that contains both `core/`
    and `exports/`, which is the standard Hive repository layout.
    """
    repo_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(repo_root))
    core_dir = repo_root / "core"
    exports_dir = repo_root / "exports"
    if core_dir.exists():
        sys.path.insert(0, str(core_dir))
    if exports_dir.exists():
        sys.path.insert(0, str(exports_dir))
    return repo_root


def _archive_export(repo_root: Path) -> Path:
    """Archive the standard Hive export folder into a zip file."""
    agent_dir = repo_root / "exports" / "analytical_advisor"
    dist_dir = repo_root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    archive_path = shutil.make_archive(
        base_name=str(dist_dir / "analytical_advisor"),
        format="zip",
        root_dir=str(agent_dir.parent),
        base_dir=agent_dir.name,
    )
    return Path(archive_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--query",
        default=(
            "I have a customer churn dataset with 18 months of account history, "
            "product usage, support tickets, and billing features. The business "
            "wants to predict churn in the next 60 days and understand the main "
            "drivers, but the positive class is only 8%."
        ),
        help="Natural-language test query to run through the agent.",
    )
    parser.add_argument(
        "--skip-demo",
        action="store_true",
        help="Only validate and archive; skip the live agent run.",
    )
    args = parser.parse_args()

    repo_root = _bootstrap_paths()

    from exports.analytical_advisor import default_agent

    validation = default_agent.validate()
    if not validation["valid"]:
        print(json.dumps(validation, indent=2))
        return 1

    print("Validation passed.")

    if not args.skip_demo:
        result = asyncio.run(default_agent.run({"user_query": args.query}))
        print(json.dumps({"success": result.success, "output": result.output, "error": result.error}, indent=2, default=str))
        if not result.success:
            return 1

    archive_path = _archive_export(repo_root)
    print(f"Archive created at: {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
