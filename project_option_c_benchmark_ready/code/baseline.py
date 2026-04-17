from __future__ import annotations
from metrics import evaluate_routes


def greedy_baseline(customers, depot, dist_matrix, time_matrix, max_vehicles=3, capacity=35):
    remaining = set(c.id for c in customers)
    cust_by_id = {c.id: c for c in customers}
    routes = [[] for _ in range(max_vehicles)]
    for v in range(max_vehicles):
        time = 0
        load = 0
        current = 0
        while remaining:
            feasible = []
            for cid in list(remaining):
                c = cust_by_id[cid]
                if load + c.demand > capacity:
                    continue
                arrival = time + int(time_matrix[current][cid])
                wait = max(0, c.ready - arrival)
                lateness = max(0, arrival - c.due)
                score = float(dist_matrix[current][cid]) + 0.6 * wait + 12 * lateness
                feasible.append((score, lateness, cid, arrival))
            if not feasible:
                break
            feasible.sort(key=lambda x: (x[1] > 0, x[0]))
            _, _, cid, arrival = feasible[0]
            c = cust_by_id[cid]
            time = max(arrival, c.ready) + c.service
            load += c.demand
            routes[v].append(cid)
            remaining.remove(cid)
            current = cid
    if remaining:
        # force append unassigned customers to shortest route
        ordered = sorted(remaining)
        for cid in ordered:
            tgt = min(range(max_vehicles), key=lambda i: len(routes[i]))
            routes[tgt].append(cid)
    metrics = evaluate_routes(routes, customers, depot, dist_matrix, time_matrix, capacity)
    return routes, metrics
