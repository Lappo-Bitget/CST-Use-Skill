---
name: cst-use
description: Create, modify, run, diagnose, and verify electromagnetic simulation projects in CST Studio Suite, especially CST 2024 Microwave Studio. Use when Codex must operate CST, build antennas/waveguides/metasurfaces/RIS or periodic unit cells, configure materials/boundaries/ports/Floquet modes/solvers, reproduce a paper model, extract S-parameters or phases, troubleshoot CST licenses and crashes, or archive solved `.cst` projects and result folders.
---

# CST_Use

Use CST as an engineering tool: produce a native project, run the real solver, inspect result items, and compare results with a physical or published expectation.

## Core workflow

1. Inspect the installed CST version, processes, licenses, existing projects, and requested output location.
2. Extract all available geometry, material, excitation, boundary, solver, mesh, and validation parameters. State assumptions for missing values; never invent hidden paper parameters silently.
3. Prefer CST's official Python API (`cst.interface.DesignEnvironment`) for deterministic project creation and result extraction. Use Windows UI control for license dialogs, visual inspection, result plots, or operations unavailable through the API.
4. Create a new native MWS project when reliable. If blank-project creation crashes, use a known-good MWS seed project, copy it, remove all seed geometry/ports/monitors/results, and verify no seed content remains.
5. Work from a short ASCII-only directory when CST cannot save under a non-ASCII Windows profile. After solving, copy both the `.cst` file and its same-name result directory to the user-designated folder, excluding `*.lok` files.
6. Save before solving, run `model3d.run_solver()`, save again, then inspect the result tree through `cst.results.ProjectFile`.
7. Do not claim success merely because CST returned. Require the expected result items and numeric samples. For multi-state models, verify trends and key frequencies, not just screenshots.
8. Leave the final solved project easy to inspect in CST when practical. Deliver the native project, associated result directory, exported CSV, assumptions, and a concise verification report.

## Completion criteria

Treat a CST task as complete only when all relevant conditions hold:

- The requested geometry and named parameters exist in the project.
- Boundaries, ports/sources, frequency range, and solver match the intended problem.
- The solver ran without a blocking pre-check error.
- Expected tree items exist, such as `1D Results\\S-Parameters` or the requested field/far-field result.
- Numeric result data can be read and contains samples.
- Results are physically plausible or compared with the provided reference.
- The `.cst` file and its external result directory are archived together.

## Safety and project hygiene

- Preserve unrelated open CST projects and user changes. Close or overwrite only projects created for the current task.
- Before reusing a seed, copy it to a new path. Never modify the seed in place.
- Do not delete components unless their names were positively identified as seed content or current-task content.
- A `Retrieve License` prompt means reacquire the released frontend license; it does not imply simulation failure. Ongoing solvers may continue using a solver license.
- Keep a status log and record exact CST errors, result item names, mesh size, solver return, and output paths.

## Resources

- Read [references/cst-2024-workstation.md](references/cst-2024-workstation.md) for this workstation's verified paths, commands, failure recovery, and Floquet setup.
- Read [references/modeling-and-validation.md](references/modeling-and-validation.md) when reproducing papers, modeling periodic/RIS structures, unwrapping phase, or judging agreement.
- Run `scripts/cst_project_tool.py inspect <project.cst>` to verify result-tree contents and export summaries.
- Run `scripts/cst_project_tool.py sync <project.cst> <destination-directory>` to copy a `.cst` project and its external result directory safely.

