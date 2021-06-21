import sys
import json
import networkx as nx
import numpy as np
from pathlib import Path
import os



gen_route_demand_stoppoint_tuple_list = []
pickup_point_list = []


def get_route_len(route):
    length = 0 
    for node in route:
        if node in pickup_point_list:
            length += 1
    return length

def get_last_touched_zone(route):
    for i in range(len(route)-1, 0, -1):
        if route[i] in pickup_point_list:
            return route[i]
    return None

def read_demand_matrix(path):
    text = path.read_text()
    numbers = list(map(float, text.split()))
    size = int(numbers[0])
    matrix = np.array(numbers[1:]).reshape(size, size)
    return matrix


def read_distance_matrix(path):
    text = path.read_text()
    numbers_tmp = list(map(float, text.split()))
    numbers = [float("inf") if number < 0 else number for number in numbers_tmp ]
    size = int(numbers[0])
    matrix = np.array(numbers[1:]).reshape(size, size)
    return matrix


def get_highest_demand_pair(demand_matrix):
    return np.unravel_index(np.argmax(demand_matrix), demand_matrix.shape)


def get_highest_demand_destination_from(source, demand_matrix):
    return np.argmax(demand_matrix[source])

def get_nonzero_lowest_demand_dst_to(dest, demand_matrix):
    valid_idx = np.where(demand_matrix[pickup_point_list,dest] > 0)[0]
    if valid_idx.shape[0] == 0:     
        return None
    node =  np.argmin(demand_matrix[valid_idx,dest])
    return pickup_point_list[node]

def get_highest_demand_dst_to(dest, demand_matrix):
    node = np.argmax(demand_matrix[pickup_point_list,dest])
    return pickup_point_list[node]

def set_demand_satisfied_in_route(demand_matrix, route, dest):
    demand_matrix = demand_matrix.copy()
    satisfied_demand = 0
    stop_point_list = []
    for i in route:
        satisfied_demand += demand_matrix[i, dest]
        if demand_matrix[i][dest] != 0:
            stop_point_list.append(i)
        demand_matrix[i][dest] = 0
    # finally include the shelter point (route last node/dest)
    stop_point_list.append(dest)
    return demand_matrix, satisfied_demand, stop_point_list


def disconnect_nodes_in_route_from_graph(graph, route):
    for i in route:
        edges_to_remove = list((i, j) for j in graph[i])
        graph.remove_edges_from(edges_to_remove)


def importance_of_node_in_between(source, dest, demand_matrix):
    demand_from_source = demand_matrix[source, :]
    demand_to_dest = demand_matrix[:, dest]
    return demand_from_source + demand_to_dest


def node_cost_from_importance(node_importance, weight):
    # return np.exp(- weight * node_importance)
    return weight / (1.0 + node_importance)


def get_best_route_between(source, dest, graph, demand_matrix, weight):
    node_importance = importance_of_node_in_between(source, dest, demand_matrix)
    node_cost = node_cost_from_importance(node_importance, weight)
    best_route = nx.algorithms.shortest_paths.weighted.dijkstra_path(graph, source, dest, weight=lambda u,v,d: node_cost[u] + node_cost[v] + d['weight'])
    return best_route


def get_route_satisfying_constraint(graph, demand_matrix, weight, min_hop_count, max_hop_count):
    graph = graph.copy()
    alter = False
    demand_matrix = demand_matrix.copy()
    source, dest = get_highest_demand_pair(demand_matrix)
    # at least these two will be stops
    stop_point_list = [source, dest]
    route = [source]
    iteration_count = 0
    while iteration_count < max_hop_count:
        source2 = dest
        if alter:
            source2 = get_nonzero_lowest_demand_dst_to(dest, demand_matrix)
        else:
            source2 = get_highest_demand_dst_to(dest, demand_matrix)

        if source2 is None:
            source2 = source
            break

        try:
            route_chunk = get_best_route_between(source, source2, graph, demand_matrix, weight)
        except nx.NetworkXNoPath as e:
            break

        route_chunk = route_chunk[1:]
        if get_route_len(route) < max_hop_count:
            route_to_dest = get_best_route_between(source2, dest, graph, demand_matrix, weight)
            if len(route_to_dest) == 2 and graph[route_to_dest[0]][route_to_dest[1]]["weight"] == float("inf"):
                break
            route.extend(route_chunk)
            # add the newly added stop point
            source
        else:
            alter = not alter
            break

        demand_matrix, _, _ = set_demand_satisfied_in_route(demand_matrix, route, dest)
        source = source2
        # source, dest = source2, get_highest_demand_destination_from(dest, demand_matrix)
        #if demand_matrix[source][dest] == 0.:
        #    break
        alter = not alter
        iteration_count += 1

    route_chunk = get_best_route_between(source, dest, graph, demand_matrix, weight)

    route.extend(route_chunk[1:])
    # followings are unnecessary as after this function will be exited and this copy of demand matrix will be lost
    # demand_matrix, _, _ = set_demand_satisfied_in_route(demand_matrix, route, dest)
    # disconnect_nodes_in_route_from_graph(graph, route[:-1])
    
    return route


def get_routes(graph, demand_matrix, weight, min_hop_count, max_hop_count):
    demand_matrix = demand_matrix.copy()
    while np.sum(demand_matrix) > 0.:
        route = get_route_satisfying_constraint(graph, demand_matrix, weight, min_hop_count, max_hop_count)
        # now to modify the demand matrix according to the serviced node's demand by this route
        # node which has still non zero demand and will be made zero should be the stoppoint of route 
        demand_matrix, satisfied_demand, stop_point_list = set_demand_satisfied_in_route(demand_matrix, route, route[-1])
        gen_route_demand_stoppoint_tuple_list.append((route, satisfied_demand, stop_point_list))
        yield route

def get_return_route(graph, src_dest_pair):
    src = src_dest_pair[1]
    dest = src_dest_pair[0]
    route = nx.algorithms.shortest_paths.weighted.dijkstra_path(graph, src, dest, weight=lambda u,v,d: d['weight'])
    return route

def save_graph_as_json(distance_matrix, file_path):
    distance_matrix1 = distance_matrix.copy()
    graph = nx.convert_matrix.from_numpy_matrix(distance_matrix1, create_using=nx.DiGraph)
    dest_path = file_path.parent/(file_path.stem + '.json')
    data = nx.readwrite.json_graph.node_link_data(graph)
    with open(dest_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return graph


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python3 main.py distance_file demand_file pickup_point_list_file max_hop_count weight")
        exit(0)

    dist_file = Path(sys.argv[1])
    if dist_file.suffix == '.json':
        with open(dist_file) as f:
            data = json.load(f)
        graph = nx.readwrite.json_graph.node_link_graph(data)
        graph_return_route_calc = graph.copy()
        distance_matrix = nx.convert_matrix.to_numpy_matrix(graph)
    else:
        distance_matrix = read_distance_matrix(dist_file)
        graph = save_graph_as_json(distance_matrix, dist_file)

    mean = lambda l: sum(l) / len(l)
    #print('Average distance: {}'.format(mean(list(map(lambda d:d[2], graph.edges.data(data='weight'))))))

    demand_file = Path(sys.argv[2])
    demand_matrix = read_demand_matrix(demand_file)

    #print('Average demand: {}'.format(demand_matrix[np.nonzero(demand_matrix)].mean()))
    #print('Total demand: {}'.format(demand_matrix.sum()))
    #print('{0}'.format(demand_matrix.sum()))

    with(open(sys.argv[3])) as pickup_point_file:
        for line in pickup_point_file.readlines():
            pickup_point_list.append(int(line.strip()))

    weight = float(sys.argv[5])
    max_hop_count = int(sys.argv[4])
    min_hop_count = 0

    routes = list(get_routes(graph, demand_matrix, weight, min_hop_count, max_hop_count))

    for route in routes:
        try:
            assert(len(route) == len(set(route)), "node repeated in route")
        except AssertionError as e:
            pass

    route_src_dest_pair_list_for_return_routes = []
    for tup in sorted(gen_route_demand_stoppoint_tuple_list, key=lambda tup: tup[1], reverse=True):
        return_route = get_return_route(graph, (tup[0][0], tup[0][-1]))
        # at first list the stop point in route
        for idx, node in enumerate(tup[2]):
            if idx > 0:
               print(' ', end='')
            print(node, end='')	
        print('')
        # then write the route node + return route node
        for idx, node in enumerate(tup[0]):
            print(node, end=' ')
        for node_id in return_route[1:]:
            print(node_id, end=' ')
        print('')

