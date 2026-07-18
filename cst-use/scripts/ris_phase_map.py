"""Generate reflectarray/RIS phase and discrete-state maps."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


C0 = 299_792_458.0


def wrap_360(value: float) -> float:
    return value % 360.0


def angular_distance(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def load_states(path: Path | None) -> list[dict]:
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    states = data["states"] if isinstance(data, dict) else data
    result = []
    for state in states:
        result.append({
            "name": str(state["name"]),
            "phase_deg": float(state["phase_deg"]),
            "magnitude": float(state.get("magnitude", 1.0)),
            "value": state.get("value", ""),
        })
    return result


def choose_state(required_phase: float, states: list[dict], phase_weight: float, magnitude_weight: float) -> dict | None:
    if not states:
        return None
    return min(
        states,
        key=lambda state: phase_weight * angular_distance(state["phase_deg"], required_phase) ** 2
        + magnitude_weight * (1.0 - state["magnitude"]) ** 2,
    )


def build_rows(args: argparse.Namespace, states: list[dict]) -> list[dict]:
    wavelength = C0 / (args.frequency_ghz * 1e9)
    k0 = 2.0 * math.pi / wavelength
    theta = math.radians(args.theta_deg)
    phi = math.radians(args.phi_deg)
    direction = (
        math.sin(theta) * math.cos(phi),
        math.sin(theta) * math.sin(phi),
        math.cos(theta),
    )
    feed = tuple(value / 1000.0 for value in (args.feed_x_mm, args.feed_y_mm, args.feed_z_mm))
    dx, dy = args.dx_mm / 1000.0, args.dy_mm / 1000.0
    rows = []
    for iy in range(args.ny):
        y = (iy - (args.ny - 1) / 2.0) * dy
        for ix in range(args.nx):
            x = (ix - (args.nx - 1) / 2.0) * dx
            z = 0.0
            feed_path = math.sqrt((x - feed[0]) ** 2 + (y - feed[1]) ** 2 + (z - feed[2]) ** 2)
            outgoing_projection = x * direction[0] + y * direction[1] + z * direction[2]
            phase = wrap_360(args.phase_offset_deg - math.degrees(k0 * feed_path) + math.degrees(k0 * outgoing_projection))
            state = choose_state(phase, states, args.phase_weight, args.magnitude_weight)
            row = {
                "ix": ix,
                "iy": iy,
                "x_mm": x * 1000.0,
                "y_mm": y * 1000.0,
                "required_phase_deg": phase,
                "feed_path_mm": feed_path * 1000.0,
            }
            if state:
                row.update({
                    "state": state["name"],
                    "state_phase_deg": state["phase_deg"],
                    "state_magnitude": state["magnitude"],
                    "state_value": state["value"],
                    "phase_error_deg": angular_distance(state["phase_deg"], phase),
                })
            rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nx", type=int, required=True)
    parser.add_argument("--ny", type=int, required=True)
    parser.add_argument("--dx-mm", type=float, required=True)
    parser.add_argument("--dy-mm", type=float, required=True)
    parser.add_argument("--frequency-ghz", type=float, required=True)
    parser.add_argument("--feed-x-mm", type=float, default=0.0)
    parser.add_argument("--feed-y-mm", type=float, default=0.0)
    parser.add_argument("--feed-z-mm", type=float, required=True)
    parser.add_argument("--theta-deg", type=float, default=0.0)
    parser.add_argument("--phi-deg", type=float, default=0.0)
    parser.add_argument("--phase-offset-deg", type=float, default=0.0)
    parser.add_argument("--states-json", type=Path)
    parser.add_argument("--phase-weight", type=float, default=1.0)
    parser.add_argument("--magnitude-weight", type=float, default=100.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.nx <= 0 or args.ny <= 0 or args.dx_mm <= 0 or args.dy_mm <= 0 or args.frequency_ghz <= 0:
        parser.error("array dimensions, spacing, and frequency must be positive")
    states = load_states(args.states_json)
    rows = build_rows(args, states)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    phase_errors = [row["phase_error_deg"] for row in rows if "phase_error_deg" in row]
    summary = {
        "elements": len(rows),
        "phase_min_deg": min(row["required_phase_deg"] for row in rows),
        "phase_max_deg": max(row["required_phase_deg"] for row in rows),
        "quantized": bool(states),
        "rms_phase_error_deg": math.sqrt(sum(value * value for value in phase_errors) / len(phase_errors)) if phase_errors else None,
        "output": str(args.output),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
