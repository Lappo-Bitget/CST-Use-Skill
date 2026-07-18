"""Inspect or safely sync CST Studio Suite projects.

Usage:
    python cst_project_tool.py inspect PROJECT.cst [--csv OUTPUT.csv]
    python cst_project_tool.py sync PROJECT.cst DESTINATION_DIRECTORY
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
import sys
from pathlib import Path


DEFAULT_CST_LIB = Path(r"C:\Program Files (x86)\CST Studio Suite 2024\AMD64\python_cst_libraries")


def load_cst_api():
    cst_lib = Path(os.environ.get("CST_PYTHON_LIB", DEFAULT_CST_LIB))
    if not cst_lib.is_dir():
        raise RuntimeError(f"CST Python API directory not found: {cst_lib}")
    sys.path.insert(0, str(cst_lib))
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(cst_lib))
    from cst.results import ProjectFile
    return ProjectFile


def inspect_project(project: Path, csv_path: Path | None) -> dict:
    ProjectFile = load_cst_api()
    result = ProjectFile(project, allow_interactive=True).get_3d()
    tree = result.get_tree_items()
    s_items = [item for item in tree if item.startswith("1D Results\\S-Parameters\\")]
    summaries = []
    csv_rows = []
    for item in s_items:
        try:
            data = result.get_result_item(item).get_data()
        except Exception as exc:
            summaries.append({"item": item, "error": str(exc)})
            continue
        numeric = []
        for sample in data:
            x, value = sample[0], sample[1]
            magnitude = abs(value)
            db = 20.0 * math.log10(max(magnitude, 1e-300))
            phase = math.degrees(math.atan2(value.imag, value.real))
            numeric.append((x, magnitude, db, phase))
            csv_rows.append([item, x, value.real, value.imag, magnitude, db, phase])
        summary = {"item": item, "samples": len(numeric)}
        if numeric:
            minimum = min(numeric, key=lambda row: row[1])
            maximum = max(numeric, key=lambda row: row[1])
            summary.update({
                "min_x": minimum[0], "min_magnitude": minimum[1], "min_dB": minimum[2],
                "max_x": maximum[0], "max_magnitude": maximum[1], "max_dB": maximum[2],
            })
        summaries.append(summary)
    if csv_path:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(["result_item", "x", "real", "imag", "magnitude", "dB", "phase_deg"])
            writer.writerows(csv_rows)
    return {
        "project": str(project),
        "tree_item_count": len(tree),
        "s_parameter_item_count": len(s_items),
        "s_parameters": summaries,
    }


def sync_project(project: Path, destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    target_project = destination / project.name
    shutil.copy2(project, target_project)
    source_results = project.with_suffix("")
    target_results = destination / source_results.name
    if source_results.is_dir():
        shutil.copytree(
            source_results,
            target_results,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("*.lok"),
        )
    return {
        "source_project": str(project),
        "target_project": str(target_project),
        "result_directory_copied": source_results.is_dir(),
        "target_result_directory": str(target_results) if source_results.is_dir() else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("project", type=Path)
    inspect_parser.add_argument("--csv", type=Path)
    sync_parser = subparsers.add_parser("sync")
    sync_parser.add_argument("project", type=Path)
    sync_parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    project = args.project.expanduser().resolve()
    if not project.is_file():
        parser.error(f"Project not found: {project}")
    if args.command == "inspect":
        output = inspect_project(project, args.csv.expanduser().resolve() if args.csv else None)
    else:
        output = sync_project(project, args.destination.expanduser().resolve())
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
