import sys
import datetime

NETWORK_NAME="halifax evacuation"

ROOT_TAG=[
"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\
<!DOCTYPE transitSchedule SYSTEM \"http://www.matsim.org/files/dtd/transitSchedule_v1.dtd\">\n\
<transitSchedule>", 
"</transitSchedule>"
]

TRANSIT_STOP_TAG=[
"<transitStops>", 
"</transitStops>"
]

TRANSIT_STOP_DESC_TAG=[
"<stopFacility id=\"{0}\" x=\"{1}\" y=\"{2}\" linkRefId=\"{3}\" isBlocking=\"{4}\"/>"
]

TRANSIT_LINE_TAG=[
"<transitLine id=\"{0}\">\n\
<transitRoute id=\"{1}\">\n\
<transportMode>{2}</transportMode>", 
"</transitRoute>\n\
</transitLine>"
]

ROUTE_PROFILE_TAG=[
"<routeProfile>", 
"</routeProfile>"
]

ROUTE_PROFILE_DESC_TAG=[
"<stop refId=\"{0}\" departureOffset=\"{1}\" arrivalOffset=\"{2}\" awaitDeparture=\"true\"/>"
]

ROUTE_TAG=[
"<route>",
"</route>"
]

ROUTE_LINK_DESC_TAG=[
"<link refId=\"{0}\"/>"
]

DEPERTURE_TAG=[
"<departures>",
"</departures>"
]

DEPERTURE_DESC_TAG=[
"<departure id=\"{0}\" departureTime=\"{1}\" vehicleRefId=\"{2}\"/>"
]

VEHICLE_ID_FORMAT = "bus_{0}"
TOTAL_BUS = 300
TRANSIT_VEHICLE_TYPE_PROP_DICT = \
{
    "bus": {"count": TOTAL_BUS, "seat": 40, "standing": 10, "length": 8}
}


node_count = 0
network_graph = []
stop_id_dict = {}
link_id_dict = {}
route_bus_count_list = []
route_list = []
allocated_upto_bus_id = 0
allocated_upto_deperture_id = 0

def create_schedule_file(file_name):
    with open(file_name, "w") as fout:
        fout.write(ROOT_TAG[0]+"\n")

        write_stop_nodes(fout)
        for idx, route in enumerate(route_list):
            write_transit_lines(fout, idx)
        
        fout.write(ROOT_TAG[1]+"\n")


def write_stop_nodes(file_stream):
    file_stream.write(TRANSIT_STOP_TAG[0]+"\n")
    for id_no in stop_id_dict:
        write_stop_desc(file_stream, stop_id)
    file_stream.write(TRANSIT_STOP_TAG[1]+"\n")

def write_stop_desc(file_stream, stop_id):
    file_stream.write(TRANSIT_STOP_DESC_TAG[0].format(
        stop_id_dict[stop_id]["id"], 
        stop_id_dict[stop_id]["x"], 
        stop_id_dict[stop_id]["y"], 
        stop_id_dict[stop_id]["linkRefId"],
        "true"
    )+'\n')


def write_transit_lines(file_stream, id_no):
    file_stream.write(TRANSIT_LINE_TAG[0].format(id_no, id_no, "pt")+"\n")
    write_route_profile(file_stream)
    write_route(file_stream)
    write_depertures(file_stream, id_no)
    file_stream.write(TRANSIT_LINE_TAG[1] + "\n")

def write_route_profile(file_stream, id_no):
    file_stream.write(ROUTE_PROFILE_TAG[0]+"\n")
    for node in route_list[id_no]:
        if node in stop_id_dict:
            file_stream.write(ROUTE_PROFILE_DESC_TAG[0].format(stop_id_dict[node]["id"], "00:00:00", "00:00:00")+'\n')
    file_stream.write(ROUTE_PROFILE_TAG[1]+"\n")

def write_route(file_stream, id_no):
    file_stream.write(ROUTE_TAG[0]+"\n")
    # go route    
    for idx, node in enumerate(route_list[id_no]):
        if idx > 0:
            file_stream.write(ROUTE_LINK_DESC_TAG[0].format(link_id_dict[(route_list[id_no][idx - 1], node)])+'\n')
    # return route
    for idx in range(len(route_list[id_no])-1, 0, -1):
        if idx > 0:
            file_stream.write(ROUTE_LINK_DESC_TAG[0].format(link_id_dict[(route_list[id_no][idx], route_list[id_no][idx - 1])])+'\n')

    file_stream.write(ROUTE_LINK_DESC_TAG[0].format(link_id_dict[(node, route_list[idx - 1])])+'\n')
    file_stream.write(ROUTE_TAG[1]+"\n")

def write_depertures(file_stream, id_no):
    file_stream.write(DEPERTURE_TAG[0]+"\n")
    for i in range(allocated_bus_id, route_list[id_no]):
        file_stream.write(DEPERTURE_DESC_TAG[0].format(
            allocated_upto_deperture_id, "00:00:00", 
            VEHICLE_ID_FORMAT.format(allocated_bus_id))+'\n')
        allocated_bus_id += 1
        allocated_upto_deperture_id += 1
    file_stream.write(DEPERTURE_TAG[1]+"\n")

def parse_network_file(network_file_path):
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

def create_link_id_dict():
    id_no = 0
    for i in range(len(network_graph)):
        for j in range(len(network_graph[i])):
            if network_graph[i][j] > 0:
                link_id_dict[(i,j)] = id_no
                if i==98 and j==104:
                    print(link_id_dict[(98,104)])
                id_no += 1


def create_stop_id_dict(pickup_point_file_path):
    with open(pickup_point_file_path) as net_file:
        lines = net_file.readlines()
        
        for idx, line in enumerate(lines):
            stop_node_id = int(line.rsplit()[0])
            stop_id_dict[stop_node_id] = { "id": str(stop_node_id) + "_" + str(idx), "x": stop_node_id*10, "y": (stop_node_id//20)*100}

def parse_route_file(route_file_path):
    with open(route_file_path) as route_file:
        lines = route_file.readlines()
        total_demand=float(lines[0])
        total_route=int(lines[1])

        for idx in range(2, len(lines), 2):
            sat_demand=float(lines[idx].rsplit()[0])

            route_nodes_str = lines[idx+1].rsplit()
            route_list.append([])
            for route_node_str in route_nodes_str:
                route_list[-1].append(int(route_node_str))
                # add linkRefId to stop_id_dict
                if len(route_list[-1]) > 1:
                    # if it is stop id at all
                    if route_list[-1][-2] in stop_id_dict:
                        if "linkRefId" not in stop_id_dict[route_list[-1][-2]]:
                            stop_id_dict[route_list[-1][-2]]["linkRefId"] = link_id_dict[(route_list[-1][-2], route_list[-1][-1])]

            route_bus_count_list.append(int(sat_demand*total_demand/total_demand))
            # there will be at least one bus
            if route_bus_count_list[-1] == 0:
                route_bus_count_list[-1] = 1

        if sum(route_bus_count_list) < TOTAL_BUS:
            route_bus_count_list[-1] += TOTAL_BUS - sum(route_bus_count_list)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 main.py distance_file pickup_point_file route_file out_path")
        exit(0)

    parse_network_file(sys.argv[1])    
    create_link_id_dict()
    create_stop_id_dict(sys.argv[2])
    parse_route_file(sys.argv[3])
    create_schedule_file(sys.argv[4])


