from __future__ import annotations
from pathlib import Path
import pandas as pd

from data import (
    load_benchmark_instance,
    to_nodes,
    build_matrix,
    add_urgent_order,
    traffic_zone_factory,
)
from baseline import greedy_baseline
from ortools_solver import solve_vrptw_ortools
from metaheuristic import simulated_annealing
from visualization import plot_routes, comparison_table_png, dashboard, dynamic_impact, create_map
from reporting import build_report

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
MAPS = ROOT / "maps"
DATA_DIR = ROOT / "data"


def run_all(customer_limit=None, sa_iterations=3000):
    FIG.mkdir(exist_ok=True, parents=True)
    MAPS.mkdir(exist_ok=True, parents=True)

    rows = []
    baseline_rows = []
    saved_dynamic = None

    # Required benchmark families for the project
    for scenario in ["C1", "R1", "RC1"]:
        depot, customers, max_vehicles, capacity = load_benchmark_instance(
            scenario,
            data_dir=DATA_DIR,
            customer_limit=customer_limit,
        )
        nodes = to_nodes(depot, customers)
        dist, time = build_matrix(nodes)

        base_routes, base_metrics = greedy_baseline(customers, depot, dist, time, max_vehicles, capacity)
        ort_routes, ort_metrics = solve_vrptw_ortools(customers, depot, dist, time, max_vehicles, capacity)
        sa_routes, sa_metrics = simulated_annealing(
            customers,
            depot,
            base_routes,
            dist,
            time,
            max_vehicles=max_vehicles,
            capacity=capacity,
            iterations=sa_iterations,
        )

        baseline_rows.append({
            "scenario": scenario,
            "method": "Baseline",
            **{k: base_metrics[k] for k in ["distance", "vehicles_used", "time_window_respect_pct", "co2_kg"]},
        })

        for method, metrics in [("OR-Tools", ort_metrics), ("Simulated Annealing", sa_metrics)]:
            rows.append({
                "scenario": scenario,
                "method": method,
                **{k: metrics[k] for k in ["distance", "vehicles_used", "time_window_respect_pct", "co2_kg"]},
            })

        if scenario == "RC1":
            saved_dynamic = (depot, customers, max_vehicles, capacity, ort_routes, ort_metrics)

    df = pd.DataFrame(rows)
    baseline_df = pd.DataFrame(baseline_rows)
    df.to_csv(ROOT / "results_comparison.csv", index=False)
    baseline_df.to_csv(ROOT / "results_baseline.csv", index=False)

    comparison_table_png(df, FIG / "comparison_table.png")
    dashboard(df, FIG / "dashboard.png")

    depot, customers, max_vehicles, capacity, ort_routes, ort_metrics = saved_dynamic
    plot_routes(depot, customers, ort_routes, "RC1 - OR-Tools initial routes", FIG / "initial_routes.png")
    create_map(depot, customers, ort_routes, MAPS / "route_map_initial.html")

    customers2, urgent = add_urgent_order(customers)
    nodes2 = to_nodes(depot, customers2)
    zone = traffic_zone_factory()
    dist2, time2 = build_matrix(nodes2, traffic_zone=zone, traffic_multiplier=1.35)
    rer_routes, rer_metrics = solve_vrptw_ortools(customers2, depot, dist2, time2, max_vehicles, capacity)

    plot_routes(
        depot,
        customers2,
        rer_routes,
        "RC1 - re-routing after urgent order + traffic",
        FIG / "rerouted_routes.png",
        highlight_id=urgent.id,
    )
    dynamic_impact(ort_metrics, rer_metrics, FIG / "dynamic_impact.png")
    create_map(depot, customers2, rer_routes, MAPS / "route_map_rerouted.html", highlight_id=urgent.id)

    dyn_df = pd.DataFrame([
        {"phase": "before", **{k: ort_metrics[k] for k in ["distance", "vehicles_used", "time_window_respect_pct", "co2_kg"]}},
        {"phase": "after", **{k: rer_metrics[k] for k in ["distance", "vehicles_used", "time_window_respect_pct", "co2_kg"]}},
    ])
    dyn_df.to_csv(ROOT / "results_dynamic.csv", index=False)

    build_report(ROOT / "rapport_ieee.pdf", df, baseline_df, dyn_df, FIG)
    print("Project build complete.")


if __name__ == "__main__":
    # Full Solomon instances are 100-customer problems.
    # For a faster local test, you can pass customer_limit=25 inside run_all().
    run_all(customer_limit=None, sa_iterations=3000)
