from __future__ import annotations
import math
import random
import copy
from metrics import evaluate_routes


def _flatten(routes):
    return [c for r in routes for c in r]


def _split_sequence(seq, customers, dist_matrix, time_matrix, max_vehicles=10, capacity=200):
    cust_by_id = {c.id: c for c in customers}
    routes = [[] for _ in range(max_vehicles)]
    vehicle = 0
    time = 0
    load = 0
    current = 0

    for cid in seq:
        if vehicle >= max_vehicles:
            routes[-1].append(cid)
            continue

        c = cust_by_id[cid]
        travel = int(time_matrix[current][cid])
        arrival = time + travel
        need_new_route = (load + c.demand > capacity) or ((arrival > c.due) and routes[vehicle])

        if need_new_route:
            vehicle += 1
            if vehicle >= max_vehicles:
                routes[-1].append(cid)
                continue
            time = 0
            load = 0
            current = 0
            arrival = int(time_matrix[current][cid])

        routes[vehicle].append(cid)
        time = max(arrival, c.ready) + c.service
        load += c.demand
        current = cid
    return routes


def simulated_annealing(
    customers,
    depot,
    seed_routes,
    dist_matrix,
    time_matrix,
    max_vehicles=10,
    capacity=200,
    iterations=3000,
    seed=42,
):
    rng = random.Random(seed)
    current_seq = _flatten(seed_routes)
    if not current_seq:
        current_seq = [c.id for c in customers]

    current_routes = _split_sequence(current_seq, customers, dist_matrix, time_matrix, max_vehicles, capacity)
    current_metrics = evaluate_routes(current_routes, customers, depot, dist_matrix, time_matrix, capacity)

    def score(metrics):
        # Strong penalties make SA respect feasibility before chasing shorter distance
        return (
            metrics["distance"]
            + 1000 * metrics["capacity_violations"]
            + 1000 * metrics["late_customers"]
            + 10 * metrics["vehicles_used"]
        )

    best_routes = copy.deepcopy(current_routes)
    best_metrics = dict(current_metrics)
    best_score = score(best_metrics)

    current_score = best_score
    temperature = 1000.0
    alpha = 0.995

    if len(current_seq) < 2:
        return best_routes, best_metrics

    for _ in range(iterations):
        cand = current_seq[:]
        i, j = sorted(rng.sample(range(len(cand)), 2))
        move = rng.random()

        # 3 neighborhood operators: swap, insert, 2-opt
        if move < 0.34:
            cand[i], cand[j] = cand[j], cand[i]
        elif move < 0.67:
            item = cand.pop(j)
            cand.insert(i, item)
        else:
            cand[i:j] = reversed(cand[i:j])

        cand_routes = _split_sequence(cand, customers, dist_matrix, time_matrix, max_vehicles, capacity)
        cand_metrics = evaluate_routes(cand_routes, customers, depot, dist_matrix, time_matrix, capacity)
        cand_score = score(cand_metrics)

        if cand_score < current_score:
            accept = True
        else:
            prob = math.exp((current_score - cand_score) / max(temperature, 1e-9))
            accept = rng.random() < prob

        if accept:
            current_seq = cand
            current_routes = cand_routes
            current_metrics = cand_metrics
            current_score = cand_score

            if cand_score < best_score:
                best_routes = copy.deepcopy(cand_routes)
                best_metrics = dict(cand_metrics)
                best_score = cand_score

        temperature *= alpha

    return best_routes, best_metrics
