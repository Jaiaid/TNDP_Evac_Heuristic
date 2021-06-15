import sys
from TransitPlanBuilder import TransitPlanBuilder
import sim_conf as CONF

distance_file_path = "../data/Halifax/HalifaxDistances.txt"
demand_file_path = "../data/Halifax/HalifaxOriginDestination.txt"
pickuppoint_file_path = "../data/Halifax/HalifaxPickupPoint.txt"
route_file_path = "exp20210530_result/halifax_5_1_result.txt"
return_route_file_path = "exp20210530_result/halifax_5_1_return_route.txt"

if  __name__ == "__main__":
    planbuilder = TransitPlanBuilder(
        link_cap=CONF.NETWORK_LANE_CAPACITY, 
        lane_count=CONF.NETWORK_ROAD_LANE_COUNT, 
        link_max_speed=CONF.NETWORK_MAX_LINK_SPEED,
        network_mode_str=CONF.NETWORK_MODE_STR
    )

    planbuilder.create_plan(
        network_file_path=distance_file_path, 
        demand_file_path=demand_file_path, 
        pickuppoint_file_path=pickuppoint_file_path, route_file_path=route_file_path, return_route_file_path=return_route_file_path, 
        vehicle_dict=CONF.TRANSIT_VEHICLE_TYPE_PROP_DICT, 
        start_time=CONF.TIME_TRANSIT_START, minute_between_start=CONF.TIME_BETWEEN_NEW_TRANSIT_RELEASE_MINUTE,
        max_roundtrip_minute=CONF.TIME_TRANSIT_RETURN_MINUTE, wait_minute_at_stop=CONF.TIME_WAITING_MIN
    )

    planbuilder.write_plan_matsim_format("matsim_input")
