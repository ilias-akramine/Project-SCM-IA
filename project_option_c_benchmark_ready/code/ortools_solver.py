from __future__ import annotations
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from metrics import evaluate_routes


def solve_vrptw_ortools(customers, depot, dist_matrix, time_matrix, max_vehicles=3, capacity=35):
    manager = pywrapcp.RoutingIndexManager(len(customers) + 1, max_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)
    demands = [0] + [c.demand for c in customers]
    windows = [(depot['ready'], depot['due'])] + [(c.ready, c.due) for c in customers]
    service = [0] + [c.service for c in customers]

    def time_cb(from_index, to_index):
        f = manager.IndexToNode(from_index)
        t = manager.IndexToNode(to_index)
        return int(time_matrix[f][t] + service[f])

    transit_idx = routing.RegisterTransitCallback(time_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)
    routing.AddDimension(transit_idx, 1000, 1000, False, 'Time')
    time_dim = routing.GetDimensionOrDie('Time')

    # customer windows
    for node in range(1, len(customers) + 1):
        index = manager.NodeToIndex(node)
        time_dim.CumulVar(index).SetRange(int(windows[node][0]), int(windows[node][1]))

    # start and end nodes for each vehicle
    for vehicle_id in range(max_vehicles):
        start = routing.Start(vehicle_id)
        end = routing.End(vehicle_id)
        time_dim.CumulVar(start).SetRange(int(depot['ready']), int(depot['due']))
        time_dim.CumulVar(end).SetRange(int(depot['ready']), int(depot['due']) + 1000)
        routing.AddVariableMinimizedByFinalizer(time_dim.CumulVar(start))
        routing.AddVariableMinimizedByFinalizer(time_dim.CumulVar(end))

    def demand_cb(from_index):
        f = manager.IndexToNode(from_index)
        return int(demands[f])

    demand_idx = routing.RegisterUnaryTransitCallback(demand_cb)
    routing.AddDimensionWithVehicleCapacity(demand_idx, 0, [capacity] * max_vehicles, True, 'Capacity')

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = 5
    solution = routing.SolveWithParameters(params)
    if not solution:
        return [[] for _ in range(max_vehicles)], {'distance': 0, 'vehicles_used': 0, 'late_customers': len(customers), 'time_window_respect_pct': 0, 'co2_kg': 0, 'capacity_violations': max_vehicles, 'details': []}

    routes = []
    for vehicle_id in range(max_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != 0:
                route.append(node)
            index = solution.Value(routing.NextVar(index))
        routes.append(route)
    metrics = evaluate_routes(routes, customers, depot, dist_matrix, time_matrix, capacity)
    return routes, metrics
