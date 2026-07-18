# RIS and tunable metasurface modeling

## Contents

- Evidence and model classification
- Unit-cell workflow
- Liquid-crystal constitutive modeling
- Bias, metal, and layer-stack fidelity
- Array synthesis and phase mapping
- CST implementation patterns
- Validation gates
- Source-derived benchmarks

## Evidence and model classification

Classify the requested device before building it:

- Passive fixed metasurface: geometry provides the phase or amplitude distribution.
- Reflective RIS/reflectarray: ground-backed unit cells control the reflected field.
- Transmissive metasurface/transmitarray: two Floquet sides and transmission phase matter.
- Absorber: ground-backed resonator targets impedance matching and reflection minima.
- Reconfigurable unit: PIN/varactor/MEMS or tunable material changes an electromagnetic state.
- Fed metasurface antenna: include feed network, coupling slots, input match, efficiency, and far field.

Do not treat communication-level RIS channel models as electromagnetic geometry. A review article can guide architecture and metrics but cannot supply missing layer dimensions.

For every paper-derived model, retain a parameter ledger with: symbol, value, unit, source page/figure/table, interpretation, and provenance class (explicit, figure-read, derived, assumed, or fitted).

## Unit-cell workflow

1. Reconstruct the exact layer order and metal placement. Preserve thin PI/alignment layers when their electrical properties are stated; otherwise record their omission.
2. Parameterize period, resonator dimensions, gaps, substrate/LC thicknesses, and conductor thickness.
3. Use x/y `unit cell` boundaries for an infinite periodic surface. For free-space normal incidence use z `expanded open` and Floquet ports. Set incident direction and polarization explicitly.
4. Sweep every intended tuning state and export the complex co- and cross-polar coefficients. Do not infer the useful polarization from mode number alone.
5. Build amplitude and consistently unwrapped phase versus frequency/state databases before constructing an array.
6. Select an operating band where the required phase span is available without unacceptable loss, rapid phase slope, or state-dependent amplitude imbalance.
7. Inspect surface currents or fields at resonances to identify the physical mode and distinguish a useful resonance from numerical or cross-polar artifacts.

For a ground-backed reflector, transmission should be negligible. For an absorber, use `A = 1 - |S11|^2` only after confirming negligible transmission. For a transmissive surface, retain both reflection and transmission power and check their balance against loss.

## Liquid-crystal constitutive modeling

Nematic liquid crystal is anisotropic. Its principal permittivities are approximately `eps_perp` and `eps_parallel`; loss can also differ by orientation. Prefer a tensor material or a director-dependent effective tensor:

`epsilon = eps_perp I + (eps_parallel - eps_perp) n n^T`

where `n` is the local director. A scalar permittivity sweep is an acceptable reduced-order model only when the paper itself uses it, the RF field and director geometry justify it, or a full electrostatic/director solution is unavailable. Label it as an effective-permittivity approximation.

Do not interpolate voltage directly to permittivity unless a measured or solved voltage-state curve is available. A higher-fidelity chain is:

1. Solve or import the bias electric field.
2. Obtain director orientation from the electrostatic/director model.
3. Rotate the dielectric tensor into the CST coordinate system.
4. Solve the RF problem for each voltage state.

Frequency dispersion matters from microwave through THz. Use values measured near the target band rather than optical or low-frequency catalog values.

Source-derived SM-54 examples from Wang Qiang's thesis (rectangular-cavity perturbation):

| Frequency (GHz) | eps_perp | tan_delta_perp | eps_parallel | tan_delta_parallel |
|---:|---:|---:|---:|---:|
| 11.06 | 2.330 | 0.0073 | 3.098 | 0.0023 |
| 14.58 | 2.326 | 0.0076 | 3.092 | 0.0039 |
| 18.25 | 2.331 | 0.0072 | 3.141 | 0.0041 |
| 21.98 | 2.380 | 0.0089 | 3.202 | 0.0048 |
| 25.78 | 2.382 | 0.0078 | 3.100 | 0.0042 |
| 29.58 | 2.401 | 0.0076 | 3.192 | 0.0042 |
| 33.37 | 2.446 | 0.0075 | 3.109 | 0.0044 |

These are material-specific benchmarks, not universal liquid-crystal constants.

## Bias, metal, and layer-stack fidelity

- Include bias lines and electrodes in RF geometry when their dimensions are non-negligible or they cross high-current regions.
- Preserve DC isolation gaps and the actual ground topology. A nominal ground with apertures or feed slots is not a PEC boundary.
- Use lossy copper for loss-sensitive millimeter-wave/THz models when conductivity is given. PEC is acceptable for an initial resonance baseline but not a final efficiency claim.
- Ensure metal thickness is several skin depths when modeling bulk copper. One cited 30 GHz design used about 2 micrometers after estimating a 0.38 micrometer skin depth. At THz frequencies, verify surface impedance, dispersion, and roughness assumptions.
- Thin alignment/PI films can shift resonance and phase. State explicitly whether they are modeled, homogenized, or omitted.

## Array synthesis and phase mapping

Compute required reflection phase from total path length and desired outgoing direction. For element position `r_mn`, feed position `r_f`, wavenumber `k0`, desired unit vector `s_hat`, and a freely chosen common phase `phi0`, a consistent convention is:

`phi_req(m,n) = wrap_360(phi0 - k0 |r_mn-r_f| + k0 s_hat dot r_mn)`

Check signs using a broadside case before generating the full array. The phase reference plane used for the unit-cell database must be consistent with the array geometry.

Map each required phase to a feasible state using complex-error or weighted phase/amplitude error, not phase alone. For example minimize:

`w_phi * angular_distance(phi_state, phi_req)^2 + w_mag * (|Gamma_state|-target_mag)^2`

For digital coding:

- 1-bit: nominal states 0 and 180 degrees.
- 2-bit: nominal states 0, 90, 180, and 270 degrees.
- 3-bit: eight 45-degree states.

Use actual simulated state phases and magnitudes, not ideal labels. Quantization, amplitude imbalance, mutual coupling, feed taper, and phase slope all affect sidelobes and scan loss.

Scale validation in stages: infinite unit cell -> small finite supercell/subarray -> full array. A 3x3 or 4x4 subarray can reveal bias and mutual-coupling effects before an expensive full model. Use embedded or supercell responses when local periodicity is poor.

For feed sizing, use feed radiation pattern and edge taper rather than an arbitrary separation. Two source-derived examples are:

- 36 GHz: 20x20 array, period 3.56 mm, aperture 71.2 mm, feed phase-center distance 56.6 mm.
- 100 GHz: aperture 32.7 mm, WR8.0 horn, feed distance about 25.6 mm in a cited design.

Treat these as benchmarks, not defaults.

## CST implementation patterns

- Unit cell: HF Frequency Domain, tetrahedral mesh, x/y Unit Cell, z Expanded Open, normal or specified oblique Floquet ports.
- Parameter sweep: create one state per effective permittivity/director angle or use CST parameter sweep; save state identifiers in exports.
- Oblique incidence: set periodic boundary angles and Floquet scan angles consistently; confirm polarization basis after scanning.
- Finite passive array: use plane wave plus open boundaries and far-field/RCS monitors.
- Fed array: model the horn or port, feed network/coupling slots, open boundaries, S11, efficiency, realized gain, sidelobes, and scan angle.
- Large arrays: use VBA/Python history generation, but verify element count, positions, state assignments, and material names from the completed model tree.

## Validation gates

### Unit cell

- Expected co-/cross-polar result items exist and contain numeric samples.
- Phase is derived from the complex coefficient and unwrapped consistently.
- Required phase span is achieved over the claimed band.
- Report worst-state magnitude/loss, not only the best state.
- Increasing effective LC permittivity should usually red-shift an LC-loaded resonance; investigate contrary trends.
- Mesh convergence is checked around metal edges, gaps, and the thin LC layer.

### Array

- The phase/state map matches the target beam by an independent array-factor calculation.
- Broadside is validated before scanned beams.
- Report realized gain, main-beam angle, 3 dB beamwidth, sidelobe level, cross-polarization, aperture efficiency, and scan loss as applicable.
- Compare ideal continuous phase, quantized phase, and full-wave results to separate quantization error from coupling/feed error.
- A solver-return message is insufficient: require far-field result items and numeric extrema.

### Paper reproduction

- Compare resonance positions, phase span, loss envelope, tuning direction, and beam angles.
- Do not force a 360-degree branch to match a paper. Reference planes and Floquet mode orientation can change absolute phase.
- Distinguish independent reconstruction from the authors' original CST project.

## Source-derived benchmarks

The following values were extracted and visually checked from the supplied Chinese sources. They are useful regression targets, not general constants:

Source roles:

- Zhang Zijian's chapter on intelligent metasurfaces and Liu Xiandi's RIS application review provide concepts, use cases, architectures, and tuning-technology comparisons. Use them for model classification and performance metrics, not for dimension-exact reconstruction unless a particular cited design is independently obtained.
- Wang Qiang's dissertation provides directly actionable millimeter-wave LC material measurements, absorber geometry, periodic-boundary settings, coding-state relations, and array results.
- Wang Pengjun's dissertation provides directly actionable 100 GHz double-dipole unit-cell settings, phase/loss benchmarks, feed/aperture design, and subarray/array workflows.
- Yin Mingjun's dissertation provides reflectarray phase synthesis, 36 GHz and 100 GHz array/feed benchmarks, subarray bias simplification, and millimeter-wave/THz phase-shifter validation.

- Wang Qiang thesis, 34-36 GHz reflective LC unit: x/y Unit Cell, z Open(add space), normal incidence, x-linear polarization, Floquet excitation, frequency-domain solve; an effective permittivity sweep around 2.5-3.1 produced a claimed 360-degree reflection span with loss below about 2.5 dB.
- Wang Qiang thesis, three-band absorber: BF33 glass `eps_r=4.65`, `tan_delta=0.001`; SM-54 LC near 30 GHz `eps_perp=2.4`, `tan_delta_perp=0.0076`, `eps_parallel=3.2`, `tan_delta_parallel=0.0042`; three cut-wire lengths 2.5/2.9/3.3 mm, widths 0.2/0.3/0.4 mm, glass thickness 0.7 mm, LC thickness 0.05 mm, bias-line width 0.1 mm, copper thickness 0.002 mm.
- Wang Pengjun thesis, 100 GHz double-dipole unit: quartz `eps_r=3.78`, `tan_delta=0.002`; LC effective permittivity 2.57-3.47 with `tan_delta=0.02`; Unit Cell and Open(add space); reported over 360 degrees across 94.8-102.1 GHz and 514.5 degrees at 99.8 GHz.
- Yin Mingjun thesis: 36 GHz 20x20 reflectarray, period 3.56 mm, 71.2 mm square aperture, 56.6 mm feed distance; reported 24.1 dBi maximum E-plane gain. A 100 GHz architecture used 3x3 subarrays to reduce bias complexity and a 32.7 mm aperture with a WR8.0 horn.
