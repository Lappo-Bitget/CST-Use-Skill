# Modeling and validation reference

## Contents

- Parameter provenance
- Paper reproduction
- Electromagnetic checks
- Multi-state phase validation
- Reporting

## Parameter provenance

Classify every model value as one of:

- Explicitly stated in the source.
- Read from a labeled figure.
- Derived from an equation or symmetry.
- Assumed because the source omits it.
- Fitted after comparison.

Keep source parameters unchanged for a baseline reproduction. If optimization is requested, save it as a separate project and report changed parameters.

## Paper reproduction

1. Extract the full text for indexing, then render and visually inspect the pages containing geometry, dimensions, layer order, curves, and boundary descriptions.
2. Record layer sequence, thicknesses, material tensor/scalar values, loss model, metal model, unit-cell period, polarization, incidence, solver, and target results.
3. If a paper omits PI properties, metal dispersion, roughness, mesh strategy, bias-line details, or a dimension convention, state the baseline assumption explicitly.
4. Reproduce representative unit cells before building large arrays. Confirm tuning direction and resonance location before scaling.
5. A project proposal or review article may describe a method without enough geometry to reproduce. Do not fabricate a second model merely to match the number of supplied documents.

## Electromagnetic checks

Use problem-specific expectations:

- Uniform lossless waveguide: very low reflection and near-unity transmission above cutoff.
- Ground-backed resonator: near-zero transmission; reflection magnitude and phase vary near resonance.
- Tunable dielectric/RIS: increasing effective permittivity usually red-shifts resonance.
- Reciprocal two-port: compare `S21` and `S12`.
- Symmetric model: compare expected symmetric S-parameters or polarizations.
- Periodic model: confirm unit-cell boundaries, normal/oblique incidence, and Floquet mode identity.

Never validate solely by a visually plausible geometry.

## Multi-state phase validation

Export the complex coefficient and calculate:

```python
phase_deg = math.degrees(math.atan2(value.imag, value.real))
```

Keep both raw phase in `[-180, 180]` and frequency-unwrapped phase. A simple unwrap increments/decrements 360 degrees when adjacent phase differences cross 180 degrees.

For phase difference at a fixed frequency, report:

- Raw state phases.
- Signed wrapped difference.
- Absolute modulo-360 difference.
- Difference between consistently unwrapped curves.

Do not choose a 360-degree branch merely to match a published value. Phase reference planes, port orientation, and mode ordering can change absolute phase. Compare resonance shift, curve shape, and phase range together.

## Reporting

Include:

- CST version and solver.
- Geometry/material/boundary assumptions.
- Project names and output paths.
- Mesh size when available.
- Exact result item names and sample counts.
- Key simulated values versus reference values with errors.
- Mismatches and likely causes.
- A statement distinguishing independent reproduction from the author's original project.

