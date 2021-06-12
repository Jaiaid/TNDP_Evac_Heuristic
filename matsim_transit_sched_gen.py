import sys
import datetime

import sim_conf as CONF

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
"<stop refId=\"{0}\" arrivalOffset=\"{1}\" departureOffset=\"{2}\" awaitDeparture=\"true\"/>"
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


node_count = 0
network_graph = []
pickuppoint_list = []
stop_id_dict = {}
link_id_dict = {}
transit_id_round_trip_count_dict = {}
route_bus_count_list = []
route_list = []
return_route_list = []
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
        write_stop_desc(file_stream, id_no)
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
    file_stream.write(TRANSIT_LINE_TAG[0].format(id_no, id_no, CONF.TRANSIT_MODE)+"\n")
    write_route_profile(file_stream, id_no)
    write_route(file_stream, id_no)
    write_depertures(file_stream, id_no)
    file_stream.write(TRANSIT_LINE_TAG[1] + "\n")


def write_route_profile(file_stream, id_no):
    # arrival offset means at which offset after starting transit will arrive
    arrival_offset = "00:00:00"
    # deperture offset means at which offset after starting transit will leave
    deperture_offset = (datetime.datetime.strptime(arrival_offset, "%H:%M:%S") + \
                             datetime.timedelta(minutes=CONF.TIME_WAITING_MIN)).strftime("%H:%M:%S")

    file_stream.write(ROUTE_PROFILE_TAG[0]+"\n")

    round_trip_count = 0
    # keep running the transit in circular as for CONF.TRANSIT_RUN_TIME_HOUR_LENGTH
    while arrival_offset < CONF.TRANSIT_RUN_TIME_HOUR_LENGTH:
        for i in range(1, len(route_list[id_no])):
            possible_stop_id = (route_list[id_no][i - 1], route_list[id_no][i])
            if possible_stop_id in stop_id_dict:
                file_stream.write(ROUTE_PROFILE_DESC_TAG[0].format(stop_id_dict[possible_stop_id]["id"], arrival_offset, deperture_offset)+'\n')
                # arrival offset means at which offset after starting transit will arrive
                arrival_offset = (datetime.datetime.strptime(arrival_offset, "%H:%M:%S") + \
                                         datetime.timedelta(minutes=CONF.TIME_WAITING_MIN + CONF.TIME_BETWEEN_STOP_MINUTE)).strftime("%H:%M:%S")
                # deperture offset means at which offset after starting transit will leave
                deperture_offset = (datetime.datetime.strptime(arrival_offset, "%H:%M:%S") + \
                                         datetime.timedelta(minutes=CONF.TIME_BETWEEN_STOP_MINUTE + CONF.TIME_WAITING_MIN)).strftime("%H:%M:%S")

        # arrival offset means at which offset after starting transit will arrive
        arrival_offset = (datetime.datetime.strptime(arrival_offset, "%H:%M:%S") + \
                                 datetime.timedelta(minutes=CONF.TIME_WAITING_MIN + CONF.TIME_BETWEEN_STOP_MINUTE)).strftime("%H:%M:%S")
        # deperture offset means at which offset after starting transit will leave
        deperture_offset = (datetime.datetime.strptime(arrival_offset, "%H:%M:%S") + \
                                 datetime.timedelta(minutes=CONF.TIME_BETWEEN_STOP_MINUTE + CONF.TIME_WAITING_MIN)).strftime("%H:%M:%S")
        # shelter stop id
        # for normal stop (stop id, next node)
        # for shelter stop (stop id, return route 2nd node)
        file_stream.write(ROUTE_PROFILE_DESC_TAG[0].format(stop_id_dict[(route_list[id_no][-1], return_route_list[id_no][1])]["id"], arrival_offset, deperture_offset)+'\n')
        # one round trip completed
        round_trip_count +=1

    transit_id_round_trip_count_dict[id_no] = round_trip_count 
    file_stream.write(ROUTE_PROFILE_TAG[1]+"\n")


def write_route(file_stream, id_no):
    file_stream.write(ROUTE_TAG[0]+"\n")
    # have to repeat the link unless all round trip are done
    for round_trip in range(transit_id_round_trip_count_dict[id_no]):
        # go route
        for idx, node in enumerate(route_list[id_no]):
            if idx > 0:
                file_stream.write(ROUTE_LINK_DESC_TAG[0].format(link_id_dict[(route_list[id_no][idx - 1], node)])+'\n')
        # return route
        for idx in range(1, len(return_route_list[id_no])):
            file_stream.write(ROUTE_LINK_DESC_TAG[0].format(link_id_dict[(return_route_list[id_no][idx-1], return_route_list[id_no][idx])])+'\n')
    # start link again    
    file_stream.write(ROUTE_LINK_DESC_TAG[0].format(link_id_dict[(route_list[id_no][0], route_list[id_no][1])])+'\n')
    file_stream.write(ROUTE_TAG[1]+"\n")


def write_depertures(file_stream, id_no):
    global allocated_upto_bus_id, allocated_upto_deperture_id

    # time for first transit to start
    transit_deperture_time = CONF.TIME_TRANSIT_START

    file_stream.write(DEPERTURE_TAG[0]+"\n")
    for i in range(route_bus_count_list[id_no]):
        file_stream.write(DEPERTURE_DESC_TAG[0].format(
            allocated_upto_deperture_id, transit_deperture_time, 
            CONF.VEHICLE_ID_FORMAT.format(allocated_upto_bus_id))+'\n')
        allocated_upto_bus_id += 1
        allocated_upto_deperture_id += 1
        # for next deperture time
        transit_deperture_time = (datetime.datetime.strptime(transit_deperture_time, "%H:%M:%S") + \
                             datetime.timedelta(minutes=CONF.TIME_BETWEEN_NEW_TRANSIT_RELEASE_MINUTE)).strftime("%H:%M:%S")

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
                id_no += 1


def create_pickuppoint_list(pickup_point_file_path):
    with open(pickup_point_file_path) as net_file:
        lines = net_file.readlines()
        
        for idx, line in enumerate(lines):
            pickuppoint_list.append(int(line.rsplit()[0]))


def parse_route_file(route_file_path, return_route_file_path):
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

            route_bus_count_list.append(int(sat_demand*CONF.TOTAL_BUS/total_demand))
            # there will be at least one bus
            if route_bus_count_list[-1] == 0:
                route_bus_count_list[-1] = 1

            parsed_route_no += 1

        if sum(route_bus_count_list) < CONF.TOTAL_BUS:
            route_bus_count_list[-1] += CONF.TOTAL_BUS - sum(route_bus_count_list)


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python3 main.py distance_file pickup_point_file route_file return_route_file out_path")
        exit(0)

    parse_network_file(sys.argv[1])
    create_link_id_dict()
    create_pickuppoint_list(sys.argv[2])
    parse_route_file(sys.argv[3], sys.argv[4])
    create_schedule_file(sys.argv[5])


