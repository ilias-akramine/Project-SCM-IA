from __future__ import annotations
import math
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from solomon_loader import load_solomon_txt, Customer


DEFAULT_BENCHMARK_FILES = {
    "C1": "C101.txt",
    "R1": "R101.txt",
    "RC1": "RC101.txt",
}


def euclidean(a, b):
    return float(math.hypot(a[0] - b[0], a[1] - b[1]))


def build_matrix(nodes, speed_factor: float = 1.0, traffic_zone=None, traffic_multiplier: float = 1.0):
    """In Solomon instances, travel time equals Euclidean distance."""
    coords = [(n["x"], n["y"]) for n in nodes]
    n = len(coords)
    dist = np.zeros((n, n), dtype=float)
    time = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = euclidean(coords[i], coords[j])
            if traffic_zone and (traffic_zone(coords[i]) or traffic_zone(coords[j])):
                d *= traffic_multiplier
            dist[i, j] = d
            time[i, j] = int(round(d * speed_factor))
    return dist, time


def load_benchmark_instance(instance_label: str, data_dir: str | Path | None = None, customer_limit: int | None = None):
    """Loads C1/R1/RC1 from Solomon files such as C101.txt, R101.txt, RC101.txt."""
    if instance_label not in DEFAULT_BENCHMARK_FILES:
        raise ValueError(f"Unsupported benchmark label: {instance_label}")

    base = Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / "data"
    file_path = base / DEFAULT_BENCHMARK_FILES[instance_label]
    depot, customers, max_vehicles, capacity = load_solomon_txt(file_path)

    if customer_limit:
        customers = customers[:customer_limit]

    return depot, customers, max_vehicles, capacity


def to_nodes(depot, customers):
    return [depot] + [c.__dict__.copy() for c in customers]


def add_urgent_order(customers):
    nxt = max(c.id for c in customers) + 1
    urgent = Customer(nxt, 82.0, 22.0, 5, 90, 150, 10)
    return customers + [urgent], urgent


def traffic_zone_factory():
    return lambda pt: pt[0] > 65 and pt[1] < 40
