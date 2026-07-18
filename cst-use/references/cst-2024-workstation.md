# CST 2024 workstation reference

## Contents

- Verified installation and API
- Reliable project lifecycle
- Known failures and recovery
- Microwave Studio history commands
- Unit-cell and Floquet setup
- Results and archiving

## Verified installation and API

- CST root: `C:\Program Files (x86)\CST Studio Suite 2024`
- Python API: `C:\Program Files (x86)\CST Studio Suite 2024\AMD64\python_cst_libraries`
- Add that directory to `PYTHONPATH` and call `os.add_dll_directory()` before importing CST modules.
- Core imports:

```python
from cst.interface import DesignEnvironment, running_design_environments
from cst.results import ProjectFile
```

Connect to an existing frontend when possible:

```python
ids = running_design_environments()
de = DesignEnvironment.connect(ids[0]) if ids else DesignEnvironment.new()
de.set_quiet_mode(False)
```

Project APIs verified on CST 2024:

```python
prj = de.open_project(path)   # or de.new_mws() when blank creation works
prj.model3d.add_to_history(title, vba_commands)
prj.save(path)
prj.model3d.run_solver()
prj.close()
```

## Reliable project lifecycle

1. Keep CST working files in an ASCII-only path such as `C:\CST_Work\<project>`.
2. Save the model before `run_solver()`.
3. Save after solver return.
4. Inspect results from the ASCII working copy.
5. Sync the `.cst` plus its extensionless sibling directory to the requested destination.
6. Exclude `Model.lok` and other `*.lok` files during sync.

On this workstation, `de.new_mws()` may cause `schematic_AMD64.exe` to crash. Known-good seed candidates may include:

- `C:\CST_Codex_WR90\CST_WR90_Clean_Solved.cst`
- A solved MWS project under the current user's `Desktop\CST_Skill_Test` directory

Always copy the seed first. Clear its previous results and named content in the copied project. Verify the navigation/result tree after conversion.

Example seed cleanup commands (adapt names to the actual seed):

```vb
DeleteResults
Monitor.Delete "Efield_10GHz"
Port.Delete "1"
Port.Delete "2"
Component.Delete "WR90_Verification"
```

Do not put `Rebuild` inside an `add_to_history` structure macro; CST 2024 reports that rebuild cannot be used there. History updates rebuild automatically.

## Known failures and recovery

### `schematic_AMD64.exe` crashed

This installation can crash on blank MWS worksheet creation. Dismiss the dialog, use a copied seed project, and continue through the official API.

### Cannot write to project directory

CST may replace the non-ASCII Windows username with `????` and fail directory creation. Solve in an ASCII path, then sync results back to the user folder.

### Quiet/Scripting mode blocks popups

Call `de.set_quiet_mode(False)` or press `Switch to Interactive Mode` through Windows UI control. Do not assume the license failed.

### Frontend License Released / Retrieve License

After roughly three idle hours CST can release the frontend license. `Retrieve License` reacquires it and unlocks the UI. Existing simulations may continue uninterrupted.

### `No incident field polarization has been defined`

This usually indicates plane-wave/template contamination in an old FSS project. Prefer a clean/known seed; otherwise remove the plane-wave source/template history and explicitly configure the intended ports or Floquet excitation.

### Unsupported history method

Use the exact error to remove or replace only the unsupported command. Verified examples:

- `FDSolver.SetCalculationType "Broadband"` is unsupported here; omit it. The solver frequency range still produces broadband S-parameter samples.
- `Rebuild` inside a structure macro is unsupported; omit it.

## Basic history command patterns

Units and frequency:

```vb
With Units
    .Geometry "mm"
    .Frequency "GHz"
    .Time "ns"
End With
ChangeSolverType "HF Frequency Domain"
Solver.FrequencyRange "90", "115"
```

Normal dielectric material:

```vb
With Material
    .Reset
    .Name "Substrate"
    .FrqType "all"
    .Type "Normal"
    .SetMaterialUnit "GHz", "mm"
    .Epsilon "3.78"
    .Mue "1.0"
    .Kappa "0.0"
    .TanD "0.002"
    .TanDFreq "100"
    .TanDGiven "True"
    .TanDModel "ConstTanD"
    .Create
End With
```

Brick:

```vb
With Brick
    .Reset
    .Name "Layer"
    .Component "Dielectrics"
    .Material "Substrate"
    .Xrange "-P/2", "P/2"
    .Yrange "-P/2", "P/2"
    .Zrange "0", "H"
    .Create
End With
```

## Unit-cell and Floquet setup

Verified normal-incidence setup:

```vb
With Boundary
    .Xmin "unit cell"
    .Xmax "unit cell"
    .Ymin "unit cell"
    .Ymax "unit cell"
    .Zmin "expanded open"
    .Zmax "expanded open"
    .Xsymmetry "none"
    .Ysymmetry "none"
    .Zsymmetry "none"
    .ApplyInAllDirections "False"
    .OpenAddSpaceFactor "0.5"
    .XPeriodicShift "0.0"
    .YPeriodicShift "0.0"
    .ZPeriodicShift "0.0"
    .PeriodicUseConstantAngles "False"
    .SetPeriodicBoundaryAngles "0", "0"
    .SetPeriodicBoundaryAnglesDirection "outward"
    .UnitCellFitToBoundingBox "True"
    .UnitCellDs1 "0.0"
    .UnitCellDs2 "0.0"
    .UnitCellAngle "90.0"
End With
With FloquetPort
    .Reset
    .SetDialogTheta "0"
    .SetDialogPhi "0"
    .SetPolarizationIndependentOfScanAnglePhi "0.0", "False"
    .SetSortCode "+beta/pw"
    .SetCustomizedListFlag "False"
    .Port "Zmin"
    .SetNumberOfModesConsidered "2"
    .SetDistanceToReferencePlane "0.0"
    .SetUseCircularPolarization "False"
    .Port "Zmax"
    .SetNumberOfModesConsidered "2"
    .SetDistanceToReferencePlane "0.0"
    .SetUseCircularPolarization "False"
End With
With FDSolver
    .SetMethod "Tetrahedral", "General purpose"
    .OrderTet "Second"
    .MeshAdaptionTet "False"
End With
```

Expected CST result names include entries such as:

```text
1D Results\S-Parameters\SZmax(1),Zmax(1)
1D Results\S-Parameters\SZmax(2),Zmax(2)
```

Do not assume mode 1 or mode 2 is the desired polarization. Inspect resonance and field orientation or compare both same-polarization reflections.

## Results and archiving

```python
pp = ProjectFile(project_path, allow_interactive=True).get_3d()
tree = pp.get_tree_items()
item = pp.get_result_item(r"1D Results\S-Parameters\S1,1")
data = item.get_data()
```

Samples can be triples `(x, complex_value, auxiliary_value)`, not just pairs. Read `sample[0]` and `sample[1]`.

The `.cst` file does not necessarily contain all results. Preserve the sibling directory with the same stem, for example:

```text
Model.cst
Model\Result\...
```
