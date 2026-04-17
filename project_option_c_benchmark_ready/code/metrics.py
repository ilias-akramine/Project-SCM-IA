from __future__ import annotations
from typing import List, Dict, Tuple
CO2_PER_KM = 0.18


def evaluate_routes(routes, customers, depot, dist_matrix, time_matrix, capacity=35):
    cust_by_id = {c.id: c for c in customers}
    details = []
    total_distance = 0.0
    late = 0
    served = 0
    capacity_violations = 0
    for vehicle_id, route in enumerate(routes, start=1):
        time = 0
        load = 0
        prev = 0
        route_distance = 0.0
        stops = []
        for cid in route:
            c = cust_by_id[cid]
            travel_t = int(time_matrix[prev][cid])
            travel_d = float(dist_matrix[prev][cid])
            arrival = time + travel_t
            start = max(arrival, c.ready)
            is_late = arrival > c.due
            if is_late:
                late += 1
            time = start + c.service
            load += c.demand
            route_distance += travel_d
            stops.append({
                'customer_id': cid,
                'arrival': arrival,
                'start_service': start,
                'due': c.due,
                'late': is_late,
            })
            prev = cid
            served += 1
        route_distance += float(dist_matrix[prev][0])
        total_distance += route_distance
        if load > capacity:
            capacity_violations += 1
        details.append({
            'vehicle_id': vehicle_id,
            'route': route,
            'distance': route_distance,
            'load': load,
            'stops': stops,
        })
    on_time_pct = 100.0 * (served - late) / served if served else 100.0
    return {
        'distance': round(total_distance, 2),
        'vehicles_used': sum(1 for r in routes if r),
        'late_customers': late,
        'time_window_respect_pct': round(on_time_pct, 2),
        'co2_kg': round(total_distance * CO2_PER_KM, 2),
        'capacity_violations': capacity_violations,
        'details': details,
    }
