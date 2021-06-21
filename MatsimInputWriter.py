from Schedule import Schedule
from os import link
from typing import List
from Agent import Agent
from NetworkRoute import NetworkRoute, NetworkRouteProfileEntry
from Vehicle import Vehicle

NETWORK_NAME="halifax evacuation"

NETWORK_ROOT_TAG=[
"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n\
<!DOCTYPE network SYSTEM \"http://www.matsim.org/files/dtd/network_v1.dtd\">\n\
<network name=\"{0}\">", 
"</network>"
]
NODE_TAG=["<nodes>", "</nodes>"]
NODE_DESCRIPTION_TAG=["<node id=\"{0}\" x=\"{1}\" y=\"{2}\"/>"]
LINK_TAG=["<links>","</links>"]
LINK_DESCRIPTION_TAG=["<link id=\"{0}\" from=\"{1}\" to=\"{2}\" length=\"{3}\" capacity=\"{4}\" \
freespeed=\"{5}\" permlanes=\"{6}\" modes=\"{7}\" />"]

POP_ROOT_TAG=[
"<?xml version=\"1.0\" ?>\n\
<!DOCTYPE plans SYSTEM \"http://www.matsim.org/files/dtd/plans_v4.dtd\">\n\
<plans>", 
"</plans>"
]
AGENT_TAG=["<person id=\"{0}\">", "</person>"]
AGENT_PLAN_TAG=["<plan selected=\"yes\">", "</plan>"]
AGENT_ACT_DESC_TAG=["<act type=\"{0}\" link=\"{1}\" x=\"{2}\" y=\"{3}\"  end_time=\"{4}\" />"]
AGENT_ACT_DESC_TAG_NO_END_TIME=["<act type=\"{0}\" link=\"{1}\" x=\"{2}\" y=\"{3}\" />"]
AGENT_LEG_DESC_TAG=["<leg mode=\"{0}\"></leg>"]

TYPE_STR1="home"
TYPE_STR2="shelter"
TYPE_STR3="pt interaction"

LEG_MODE_PT_STR="pt"
LEG_MODE_WALK_STR="walk"

VEHICLE_ROOT_TAG=[
"<vehicleDefinitions xmlns=\"http://www.matsim.org/files/dtd\"\n\
 xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n\
 xsi:schemaLocation=\"http://www.matsim.org/files/dtd http://www.matsim.org/files/dtd/vehicleDefinitions_v1.0.xsd\">", 
"</vehicleDefinitions>"
]

TRANSIT_DESC_TAG=[
"<vehicleType id=\"{0}\">\n\
<description>{1}</description>\n\
<capacity>\n\
<seats persons=\"{2}\"/>\n\
<standingRoom persons=\"{3}\"/>\n\
</capacity>\n\
<length meter=\"{4}\"/>\n\
<doorOperation mode=\"serial\"/>\n\
<passengerCarEquivalents pce=\"{5}\"/>\n\
</vehicleType>"
]

TRANSIT_VEHICLE_TAG=["<vehicle id=\"{0}\" type=\"{1}\"/>"]

NETWORK_NAME="halifax evacuation"

SCHEDULE_ROOT_TAG=[
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

class MatsimInputWriter:
    def write_plan_file(self, output_path: str, agent_dict: dict):
        with open(output_path, "w") as fout:
            fout.write(POP_ROOT_TAG[0]+"\n")
            self.__write_persons_tag(fout, agent_dict)
            fout.write(POP_ROOT_TAG[1]+"\n")

    def write_network_file(self, output_path: str, link_dict: dict, node_dict: dict):
        with open(output_path, "w") as fout:
            fout.write(NETWORK_ROOT_TAG[0].format(NETWORK_NAME)+"\n")
            self.__write_nodes_tag(fout, node_dict)
            self.__write_links_tag(fout, link_dict)
            fout.write(NETWORK_ROOT_TAG[1]+"\n")

    def write_vehicle_file(self, output_path: str, vehicle_list):
        with open(output_path, "w") as fout:
            fout.write(VEHICLE_ROOT_TAG[0]+"\n")

            self.__write_vehicle_desc(
                fout, vehicle_list[0].typename, vehicle_list[0].typename, vehicle_list[0].seat, 
                vehicle_list[0].standing, vehicle_list[0].length, vehicle_list[0].pce
            )

            for vehicle in vehicle_list:
                self.__write_pervehicle_entry(
                    fout, vehicle.id, vehicle.typename)

            fout.write(VEHICLE_ROOT_TAG[1]+"\n")

    def write_schedule_file(self, output_path: str, route_dict: dict):
        with open(output_path, "w") as fout:
            fout.write(SCHEDULE_ROOT_TAG[0]+"\n")

            self.__write_stop_nodes(fout, route_dict)
            for route_id in route_dict:
                route = route_dict[route_id]
                self.__write_transit_lines(fout, route)

            fout.write(SCHEDULE_ROOT_TAG[1]+"\n")

    def __write_stop_nodes(self, file_stream, route_dict: dict):
        file_stream.write(TRANSIT_STOP_TAG[0]+"\n")
        all_stops = []
        for route_id in route_dict:
            route = route_dict[route_id]
            for stopfacility in route.get_stopfacilities():
                all_stops.append(stopfacility)
        for stopfacility in set(all_stops):
            self.__write_stop_desc(file_stream, stopfacility)
        file_stream.write(TRANSIT_STOP_TAG[1]+"\n")

    def __write_stop_desc(self, file_stream, stopfacility):
        file_stream.write(TRANSIT_STOP_DESC_TAG[0].format(
            stopfacility.id, 
            stopfacility.link.origin.x, 
            stopfacility.link.origin.y, 
            stopfacility.link.id,
            stopfacility.is_blocking
        )+'\n')

    def __write_transit_lines(self, file_stream, route: NetworkRoute):
        file_stream.write(TRANSIT_LINE_TAG[0].format(route.id, route.id, route.transit_mode)+"\n")
        self.__write_route_profile(file_stream, route.profilelist)
        self.__write_route(file_stream, route)
        self.__write_depertures(file_stream, route.deperture_list)
        file_stream.write(TRANSIT_LINE_TAG[1] + "\n")

    def __write_route_profile(self, file_stream, profilelist: List[NetworkRouteProfileEntry]):
        file_stream.write(ROUTE_PROFILE_TAG[0]+"\n")

        for profile in profilelist:
            file_stream.write(
                ROUTE_PROFILE_DESC_TAG[0].format(
                    profile.stopfacility.id, profile.arrival_offset, 
                    profile.deperture_offset
                ) + '\n'
            )
        
        file_stream.write(ROUTE_PROFILE_TAG[1]+"\n")

    def __write_route(self, file_stream, route: NetworkRoute):
        file_stream.write(ROUTE_TAG[0]+"\n")
        # have to repeat the link unless all round trip are done
        for round_trip in range(route.round_trip_count):
            # go route
            for link in route.route_link_list:
                file_stream.write(
                    ROUTE_LINK_DESC_TAG[0].format(
                        link.id
                    ) + '\n'
                )
        # start link again    
        file_stream.write(
            ROUTE_LINK_DESC_TAG[0].format(
                route.route_link_list[0].id
            ) + '\n'
        )
        file_stream.write(ROUTE_TAG[1]+"\n")

    def __write_depertures(self, file_stream, deperture_list: List[Schedule]):
        file_stream.write(DEPERTURE_TAG[0]+"\n")
        for schedule in deperture_list:
            file_stream.write(
                DEPERTURE_DESC_TAG[0].format(
                    schedule.id, schedule.start_time, 
                    schedule.vehicle.id
                ) + '\n'
            )
        file_stream.write(DEPERTURE_TAG[1]+"\n")


    def __write_vehicle_desc(self, file_stream, type_id, name, seat, standing_cap, length, pce):
        file_stream.write(TRANSIT_DESC_TAG[0].format(type_id, name, seat, standing_cap, length, pce)+'\n')

    def __write_pervehicle_entry(self, file_stream, id_no, type_no):
        file_stream.write(TRANSIT_VEHICLE_TAG[0].format(id_no, type_no)+'\n')

    def __write_nodes_tag(self, file_stream, __node_dict: dict):
        file_stream.write(NODE_TAG[0]+'\n')
        for node_id in __node_dict:
            self.__write_node_desc(
                file_stream, id_no=node_id, x=__node_dict[node_id].x, y=__node_dict[node_id].y
            )
        file_stream.write(NODE_TAG[1]+'\n')

    def __write_node_desc(self, file_stream, id_no, x, y):
        file_stream.write(NODE_DESCRIPTION_TAG[0].format(id_no, x, y)+'\n')

    def __write_links_tag(self, file_stream, link_dict: dict):
        file_stream.write(LINK_TAG[0]+'\n')
        for link_id in link_dict:
            link = link_dict[link_id]
            self.__write_link_desc(
                file_stream, link.id, link.origin.id, link.dest.id, 
                link.length, link.capacity, link.speed, link.lane_count, 
                link.mode
            )
        file_stream.write(LINK_TAG[1]+'\n')

    def __write_link_desc(self, file_stream, id_no, src_id, dest_id, length, cap, speed, lane_count, mode_str):
        file_stream.write(LINK_DESCRIPTION_TAG[0].format(id_no, src_id, dest_id, length, cap, speed, lane_count, mode_str)+'\n')

    def __write_persons_tag(self, file_stream, agent_dict):
        for agent_id in agent_dict:
            agent = agent_dict[agent_id]

            file_stream.write(AGENT_TAG[0].format(agent_id)+'\n')
            file_stream.write(AGENT_PLAN_TAG[0]+'\n')
            self.__write_act_desc(file_stream, TYPE_STR1, agent.home_link.id, agent.home_link.origin.x, agent.home_link.origin.y, "07:45:00")
            #self.__write_leg_desc(file_stream, LEG_MODE_WALK_STR, start_link_id=agent.home_link.id, end_link_id=agent.stoplink.id)
            #self.__write_act_desc(file_stream, TYPE_STR3, agent.stoplink.id, agent.stoplink.origin.x, agent.stoplink.origin.y, None)
            self.__write_leg_desc(file_stream, LEG_MODE_PT_STR)
            #self.__write_act_desc(file_stream, TYPE_STR3, agent.stoplink.id, agent.shelter_link.origin.x, agent.shelter_link.origin.y, None)
            #self.__write_leg_desc(file_stream, LEG_MODE_WALK_STR, start_link_id=agent.shelter_link.id, end_link_id=agent.shelter_link.id)
            self.__write_act_desc(file_stream, TYPE_STR2, agent.shelter_link.id, agent.shelter_link.origin.x, agent.shelter_link.origin.y, None)
            file_stream.write(AGENT_PLAN_TAG[1]+'\n')
            file_stream.write(AGENT_TAG[1]+'\n')
            
    def __write_act_desc(self, file_stream, type_str, link_id, x, y, end_time):
        if end_time is None:
            file_stream.write(AGENT_ACT_DESC_TAG_NO_END_TIME[0].format(type_str, link_id, x, y)+'\n')
        else:
            file_stream.write(AGENT_ACT_DESC_TAG[0].format(type_str, link_id, x, y, end_time)+'\n')

    def __write_leg_desc(self,file_stream, mode_str):
        file_stream.write(AGENT_LEG_DESC_TAG[0].format(mode_str)+'\n')
