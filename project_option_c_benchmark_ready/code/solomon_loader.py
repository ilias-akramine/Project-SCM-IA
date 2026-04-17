from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, List


@dataclass
class Customer:
    id: int
    x: float
    y: float
    demand: int
    ready: int
    due: int
    service: int


def load_solomon_txt(file_path: str | Path) -> tuple[dict, list[Customer], int, int]:
    """Reads a Solomon VRPTW .txt file.

    Expected format:
    - line 1: instance name
    - VEHICLE block with number and capacity
    - CUSTOMER block with:
      CUST NO., XCOORD., YCOORD., DEMAND, READY TIME, DUE DATE, SERVICE TIME
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Benchmark file not found: {path}. "
            "Place Solomon files such as C101.txt, R101.txt, RC101.txt in the data/ folder."
        )

    lines = [line.rstrip("\n") for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()]
    if not lines:
        raise ValueError(f"Empty file: {path}")

    instance_name = lines[0].strip() or path.stem

    # Parse vehicle information
    max_vehicles = None
    vehicle_capacity = None
    for idx, line in enumerate(lines):
        if line.strip().upper() == "VEHICLE":
            # Usually two lines later we have "NUMBER CAPACITY", then values
            for j in range(idx + 1, min(idx + 6, len(lines))):
                parts = lines[j].split()
                if len(parts) >= 2 and all(p.replace("-", "").isdigit() for p in parts[:2]):
                    max_vehicles = int(parts[0])
                    vehicle_capacity = int(parts[1])
                    break
            break

    if max_vehicles is None or vehicle_capacity is None:
        raise ValueError(f"Could not parse VEHICLE section in {path}")

    # Parse customer table
    start_idx = None
    for idx, line in enumerate(lines):
        if "CUST NO." in line.upper():
            start_idx = idx + 1
            break
    if start_idx is None:
        raise ValueError(f"Could not locate CUSTOMER section in {path}")

    rows = []
    for line in lines[start_idx:]:
        parts = line.split()
        if len(parts) < 7:
            continue
        try:
            rows.append({
                "id": int(parts[0]),
                "x": float(parts[1]),
                "y": float(parts[2]),
                "demand": int(float(parts[3])),
                "ready": int(float(parts[4])),
                "due": int(float(parts[5])),
                "service": int(float(parts[6])),
            })
        except ValueError:
            continue

    if not rows:
        raise ValueError(f"No customer rows parsed from {path}")

    depot_row = rows[0]
    depot = {
        "id": 0,
        "x": depot_row["x"],
        "y": depot_row["y"],
        "ready": depot_row["ready"],
        "due": depot_row["due"],
        "service": depot_row["service"],
    }
    customers = [
        Customer(
            id=row["id"],
            x=row["x"],
            y=row["y"],
            demand=row["demand"],
            ready=row["ready"],
            due=row["due"],
            service=row["service"],
        )
        for row in rows[1:]
    ]
    return depot, customers, max_vehicles, vehicle_capacity
