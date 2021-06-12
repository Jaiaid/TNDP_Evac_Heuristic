import sys

NETWORK_NAME="halifax evacuation"

POP_TAG=[
"<?xml version=\"1.0\" ?>\n\
<!DOCTYPE plans SYSTEM \"http://www.matsim.org/files/dtd/plans_v4.dtd\">\n\
<plans>", 
"</plans>"
]
AGENT_TAG=["<person id=\"{0}\">", "</person>"]
AGENT_PLAN_TAG=["<plan selected=\"yes\">", "</plan>"]
AGENT_ACT_DESC_TAG=["<act type=\"{0}\" link=\"{1}\" x=\"{2}\" y=\"{3}\"  end_time=\"{4}\" />"]
AGENT_ACT_DESC_TAG_NO_END_TIME=["<act type=\"{0}\" link=\"{1}\" x=\"{2}\" y=\"{3}\" />"]
AGENT_LEG_DESC_TAG=["<leg mode=\"{0}\"/>"]

TYPE_STR1="home"
TYPE_STR2="shelter"
TYPE_STR3="pt interaction"

LEG_MODE_PT_STR="pt"
LEG_MODE_WALK_STR="transit_walk"

node_count = 0
demand_graph = []
pickuppoint_list = []
stop_id_dict = {} 
nearest_stop_dict = {}
network_graph = []
link_id_dict = {}
route_list = []
return_route_list = []
node_coordinate_dict = {}


def create_pop_file(file_name):
    with open(file_name, "w") as fout:
        fout.write(POP_TAG[0]+"\n")
        write_persons_tag(fout)
        fout.write(POP_TAG[1]+"\n")


def write_persons_tag(file_stream):
    id_no = 0
    for route_idx, route in enumerate(route_list):
        for idx, node in enumerate(route):
            if idx == 0:
                continue
            if demand_graph[route[idx-1]][route[-1]] > 0:
                person_count = int(demand_graph[route[idx-1]][route[-1]])

                link_id = link_id_dict[(route[idx-1], node)]
                destination_link_id = link_id_dict[(route[-1], return_route_list[route_idx][1])]                
                nearest_stop_link_id = link_id_dict[nearest_stop_dict[(route[idx-1], node)]]
                nearest_stop_link = nearest_stop_dict[(route[idx-1], node)]

                for i in range(person_count):
                    file_stream.write(AGENT_TAG[0].format(id_no)+'\n')
                    file_stream.write(AGENT_PLAN_TAG[0]+'\n')
                    write_act_desc(file_stream, TYPE_STR1, link_id, node_coordinate_dict[route[idx-1]][0], node_coordinate_dict[route[idx-1]][1], "07:45:00")
                    #write_leg_desc(file_stream, LEG_MODE_WALK_STR)
                    #write_act_desc(file_stream, TYPE_STR3,
                    #    nearest_stop_link_id,
                    #    node_coordinate_dict[nearest_stop_link[0]][0], 
                    #    node_coordinate_dict[nearest_stop_link[0]][1])
                    write_leg_desc(file_stream, LEG_MODE_PT_STR)
                    #write_act_desc(file_stream, TYPE_STR3, destination_link_id, node_coordinate_dict[route[-1]][0], node_coordinate_dict[route[-1]][1])
                    #write_leg_desc(file_stream, LEG_MODE_WALK_STR)
                    write_act_desc(file_stream, TYPE_STR2, destination_link_id, node_coordinate_dict[route[-1]][0], node_coordinate_dict[route[-1]][1], None)
                    file_stream.write(AGENT_PLAN_TAG[1]+'\n')
                    file_stream.write(AGENT_TAG[1]+'\n')
                    id_no += 1
                # this person plans are written make it zero so overlapped nodes are not written multiple times
                demand_graph[route[idx-1]][route[-1]] = 0


def write_act_desc(file_stream, type_str, link_id, x, y, end_time):
    if end_time is None:
        file_stream.write(AGENT_ACT_DESC_TAG_NO_END_TIME[0].format(type_str, link_id, x, y)+'\n')
    else:
        file_stream.write(AGENT_ACT_DESC_TAG[0].format(type_str, link_id, x, y, end_time)+'\n')


def write_leg_desc(file_stream, mode_str):
    file_stream.write(AGENT_LEG_DESC_TAG[0].format(mode_str)+'\n')


def create_pickuppoint_list(pickup_point_file_path):
    with open(pickup_point_file_path) as net_file:
        lines = net_file.readlines()
        
        for idx, line in enumerate(lines):
            pickuppoint_list.append(int(line.rsplit()[0]))


def calc_euclid_dist(coord1, coord2):
    return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)**0.5 


def create_nearest_stop_dict():
    for route in route_list:
        for i in range(1, len(route)):
            mindist = float("inf")
            nearest_stop = None
            for j in range(1, len(route)):
                possible_stop_node_id = (route[j-1], route[j])
                if possible_stop_node_id in stop_id_dict:
                    dist = calc_euclid_dist(node_coordinate_dict[route[i-1]], node_coordinate_dict[route[j-1]])
                    if dist < mindist:
                        nearest_stop = possible_stop_node_id
                        mindist = dist
            assert nearest_stop is not None, "{0}".format((route[i-1], route[i]))
            nearest_stop_dict[(route[i-1], route[i])] = nearest_stop 


def create_link_id_dict(network_file_path):
    with open(network_file_path) as net_file:
        lines = net_file.readlines()
        node_count=int(lines[0])

        for idx, line in enumerate(lines[1:]):
            number_strings=line.rsplit()
            assert node_count==len(number_strings), "row {0} has less entry (={1}) than node count (={2})".format(idx, len(number_strings), node_count)

            network_graph.append([])
            for number_string in number_strings:
                network_graph[-1].append(float(number_string))

            assert len(network_graph[-1])==node_count

        assert len(network_graph)==node_count

    id_no = 0
    for i in range(len(network_graph)):
        for j in range(len(network_graph[i])):
            if network_graph[i][j] > 0:
                link_id_dict[(i,j)] = id_no
                id_no += 1

        node_coordinate_dict[i] = (i*10, (i//20)*100)


def create_pickuppoint_list(pickup_point_file_path):
    with open(pickup_point_file_path) as net_file:
        lines = net_file.readlines()
        
        for idx, line in enumerate(lines):
            pickuppoint_list.append(int(line.rsplit()[0]))


def create_route_data(route_file_path, return_route_file_path):
    with open(return_route_file_path) as return_route_file:
        for line in return_route_file.readlines():
            route_nodes_str = line.rsplit()
            return_route_list.append([])
            for route_node_str in route_nodes_str:
                return_route_list[-1].append(int(route_node_str))

    # this is used to add shelter stop linkrefid, which is got by (shelter id, corresponding return route 2nd node)
    # return_route_list should be in corresponding sequence as route
    parsed_route_no = 0
    with open(route_file_path) as route_file:
        lines = route_file.readlines()
        total_demand = float(lines[0])
        total_route = int(lines[1])

        for idx in range(2, len(lines), 2):
            sat_demand=float(lines[idx].rsplit()[0])

            route_nodes_str = lines[idx+1].rsplit()
            route_list.append([])
            for route_node_str in route_nodes_str:
                route_list[-1].append(int(route_node_str))

                # add linkRefId to stop_id_dict
                if len(route_list[-1]) > 1:
                    # if it is stop id at all
                    if route_list[-1][-2] in pickuppoint_list:
                        stop_node_id = (route_list[-1][-2], route_list[-1][-1])
                        stop_id_dict[stop_node_id] = { "id": str(route_list[-1][-2]) + "_" + str(route_list[-1][-1]), "x": stop_node_id[0]*10, "y": (stop_node_id[0]//20)*100}
                        stop_id_dict[stop_node_id]["linkRefId"] = link_id_dict[(route_list[-1][-2], route_list[-1][-1])]

            # create a stop at shelter
            assert route_list[-1][-1] == return_route_list[parsed_route_no][0]
            shelter_stop_id = (route_list[-1][-1], return_route_list[parsed_route_no][1])
            stop_id_dict[shelter_stop_id] = { "id": str(route_list[-1][-1]) + "_" + str(return_route_list[parsed_route_no][1]), "x": shelter_stop_id[0]*10, "y": (shelter_stop_id[0]//20)*100}
            stop_id_dict[shelter_stop_id]["linkRefId"] = link_id_dict[(route_list[-1][-1], return_route_list[parsed_route_no][1])]

            parsed_route_no += 1


def create_demand_graph(demand_file_path):
    with open(demand_file_path) as demand_file:
        lines = demand_file.readlines()
        node_count=int(lines[0])

        for idx, line in enumerate(lines[1:]):
            number_strings=line.rsplit()
            assert node_count==len(number_strings), "row {0} has less entry (={1}) than node count (={2})".format(idx, len(number_strings), node_count)

            demand_graph.append([])
            for number_string in number_strings:
                demand_graph[-1].append(float(number_string))

            assert len(demand_graph[-1])==node_count

        assert len(demand_graph)==node_count


if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Usage: python3 main.py demand_file pickuppoint_file distance_file route_file return_route_file out_path")
        exit(0)

    create_demand_graph(sys.argv[1])
    create_pickuppoint_list(sys.argv[2])
    create_link_id_dict(sys.argv[3])
    create_route_data(sys.argv[4], sys.argv[5])
    create_nearest_stop_dict()
    create_pop_file(sys.argv[6])

