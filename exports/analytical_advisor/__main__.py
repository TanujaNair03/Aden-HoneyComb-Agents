"""CLI entry point for the Analytical Advisor agent."""

import argparse
import asyncio
import json
import shutil
import sys
from pathlib import Path
from typing import Optional

TEST_QUERY = (
    "I have a customer churn dataset with 18 months of account history, product usage, "
    "support tickets, and billing features. The business wants to predict churn in the "
    "next 60 days and understand the main drivers, but the positive class is only 8%."
)


def _render_markdown(output: dict) -> str:
    """Convert the structured Hive output into the 3 required marketplace sections."""
    sections: list[str] = []

    sections.append("## Recommended Analytical Techniques")
    for item in output.get("recommended_analytical_techniques", []):
        sections.append(f"- **{item['technique']}**: {item['why']}")

    sections.append("")
    sections.append("## Key Assumptions")
    for item in output.get("key_assumptions", []):
        sections.append(f"- **{item['assumption']}**: {item['relevance']}")

    sections.append("")
    sections.append("## Workflow Choices")
    for index, item in enumerate(output.get("workflow_choices", []), start=1):
        sections.append(f"{index}. **{item['step']}**: {item['details']}")

    return "\n".join(sections)


def _archive_export_dir(output_dir: Optional[Path] = None) -> Path:
    """
    Zip the standard Hive export directory for marketplace upload.

    Hive's first-class export unit is the agent folder under exports/. This helper
    archives that folder into a single .zip artifact so it is easy to upload.
    """
    package_dir = Path(__file__).resolve().parent
    output_dir = output_dir or package_dir.parent.parent / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)

    archive_base = output_dir / package_dir.name
    archive_path = shutil.make_archive(
        base_name=str(archive_base),
        format="zip",
        root_dir=str(package_dir.parent),
        base_dir=package_dir.name,
    )
    return Path(archive_path)


def _run_agent(query: str, as_json: bool) -> int:
    from .agent import default_agent

    result = asyncio.run(default_agent.run({"user_query": query}))
    payload = {
        "success": result.success,
        "steps_executed": result.steps_executed,
        "output": result.output,
    }
    if result.error:
        payload["error"] = result.error

    if as_json or not result.success:
        print(json.dumps(payload, indent=2, default=str))
        return 0 if result.success else 1

    print(_render_markdown(result.output))
    return 0


def _demo_agent(as_json: bool) -> int:
    from .agent import default_agent

    result = asyncio.run(default_agent.run({"user_query": TEST_QUERY}))
    payload = {
        "test_query": TEST_QUERY,
        "success": result.success,
        "steps_executed": result.steps_executed,
        "output": result.output,
    }
    if result.error:
        payload["error"] = result.error

    if as_json or not result.success:
        print(json.dumps(payload, indent=2, default=str))
        return 0 if result.success else 1

    print(f"Test query:\n{TEST_QUERY}\n")
    print(_render_markdown(result.output))
    return 0


def _info(output_json: bool) -> int:
    from .agent import default_agent

    info_data = default_agent.info()
    if output_json:
        print(json.dumps(info_data, indent=2))
        return 0

    print(f"Agent: {info_data['name']}")
    print(f"Version: {info_data['version']}")
    print(f"Description: {info_data['description']}")
    print(f"Nodes: {', '.join(info_data['nodes'])}")
    print(f"Entry: {info_data['entry_node']}")
    print(f"Terminal: {', '.join(info_data['terminal_nodes'])}")
    return 0


def _validate() -> int:
    from .agent import default_agent

    validation = default_agent.validate()
    if validation["valid"]:
        print("Agent is valid")
        return 0

    print("Agent has errors:")
    for error in validation["errors"]:
        print(f"  ERROR: {error}")
    return 1


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analytical Advisor - Hive agent for statistical method guidance."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the agent on a user query.")
    run_parser.add_argument("--query", "-q", required=True, help="Natural-language data problem")
    run_parser.add_argument("--json", action="store_true", help="Emit raw result JSON")

    demo_parser = subparsers.add_parser("demo", help="Run a built-in test query.")
    demo_parser.add_argument("--json", action="store_true", help="Emit raw result JSON")

    archive_parser = subparsers.add_parser(
        "archive", help="Package the exported agent into a .zip file."
    )
    archive_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory where the zip file should be written.",
    )

    info_parser = subparsers.add_parser("info", help="Show agent metadata.")
    info_parser.add_argument("--json", action="store_true", help="Emit metadata as JSON")

    subparsers.add_parser("validate", help="Validate the agent graph.")

    args = parser.parse_args(argv)

    if args.command == "run":
        return _run_agent(args.query, args.json)
    if args.command == "demo":
        return _demo_agent(args.json)
    if args.command == "archive":
        print(str(_archive_export_dir(args.output_dir)))
        return 0
    if args.command == "info":
        return _info(args.json)
    if args.command == "validate":
        return _validate()

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
