# Native editable geometry and Boolean history

Use this procedure when a CST project must support editing primitive dimensions through the History Tree rather than only rebuilding the model from a script.

## Create native editable primitives

Create one primitive in each `model3d.add_to_history` call. Use CST's native caption convention and a single matching primitive command:

```python
project.model3d.add_to_history(
    "define brick: Metals:Ground",
    '''With Brick
    .Reset
    .Name "Ground"
    .Component "Metals"
    .Material "PEC"
    .Xrange "-P/2", "P/2"
    .Yrange "-P/2", "P/2"
    .Zrange "Hq", "Hq+Hm"
    .Create
End With''',
)
```

Do not place several `Brick.Create` commands in one history entry such as `Create geometry`, `Metal pattern`, or `Layered dielectrics`. CST can rebuild such a block but may show `Not editable history block` and disable primitive editing.

Before replacing geometry in a solved seed project, call `project.model3d.DeleteResults()` when appropriate. This avoids the `Results May Get Incompatible With Model` prompt and prevents stale results from being presented as current.

## UI acceptance test

Do not treat parameter existence, successful rebuild, save success, or a JSON history dump as proof that a solid is editable. Verify it in CST:

1. Expand `Components` and the target component in Navigation Tree.
2. Double-click the solid, such as `Ground`, to open History Tree.
3. Select the child step `Define brick`, not the top-level `Metals:Ground` node. The top-level node normally leaves `Edit...` disabled.
4. Confirm `Edit...` becomes enabled.
5. Open it and confirm the native Brick dialog exposes the expected expressions for `Xmin`, `Xmax`, `Ymin`, `Ymax`, `Zmin`, and `Zmax`.
6. Cancel without changing values unless modification is part of the task.

If History Tree still reports `Not editable history block`, rebuild the affected primitive as a one-command native node. If the API-generated node still cannot open its editor, use Computer Use to create the primitive through CST's Modeling UI, then repeat the acceptance test immediately.

## Same-material overlap and Boolean operations

Use Boolean union only for solids with the same material and positive-volume overlap that are intended to form one conductor or dielectric body. Do not union layers that merely share a face. Do not union different materials unless the physical model explicitly requires replacing them with one chosen material.

Keep each union as its own named History node after the primitive nodes:

```python
project.model3d.add_to_history(
    "boolean add shapes: Metals:Dipole_1, Metals:Bias_line",
    'Solid.Add "Metals:Dipole_1", "Metals:Bias_line"',
)
project.model3d.add_to_history(
    "boolean add shapes: Metals:Dipole_1, Metals:Dipole_2",
    'Solid.Add "Metals:Dipole_1", "Metals:Dipole_2"',
)
```

The first argument to `Solid.Add` is the surviving target solid; the second is the consumed tool solid. After rebuilding, verify:

- the target solid remains in Navigation Tree;
- consumed tool solids no longer appear as final solids;
- initial primitive steps remain visible in History Tree;
- Boolean Add steps follow them and can be inspected;
- the resulting geometry has no unintended gaps, duplicate volumes, or material changes.

For a chain of unions, always use the surviving target in subsequent operations. Preserve separate solids where electrical isolation, a material interface, a discrete port gap, or independent parameter control is physically required.
