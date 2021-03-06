import sys
import argparse
from TransitPlanBuilder import TransitPlanBuilder
import sim_conf as CONF

if  __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data generator for matsim")
    parser.add_argument("-nf", "--network_file", help="file path containing network distance information in 2d matrix", required=True)
    parser.add_argument("-df", "--demand_file", help="file path containing network demand information in 2d matrix", required=True)
    parser.add_argument("-pf", "--pickuppoint_file", help="file path containing pickuppoint id (corresponding to given network graph row position)", required=True)
    parser.add_argument("-rf", "--route_file", help="file path containing all forward route, satisfied demand by route information", required=True)
    parser.add_argument("-mo", "--matsim_data_output_dir", help="output directory path to dump generated data for matsim", required=False)
    parser.add_argument("-smret", "--same_return_route", help="if backward route should be forward route in reverse", required=False, default=False)
    parser.add_argument("-co", "--customsim_data_output_dir", help="output directory path to dump generated data for custom simulator", required=False)

    args = vars(parser.parse_args())

    planbuilder = TransitPlanBuilder(
        link_cap=CONF.NETWORK_LANE_CAPACITY, 
        lane_count=CONF.NETWORK_ROAD_LANE_COUNT, 
        link_max_speed=CONF.NETWORK_MAX_LINK_SPEED,
        network_mode_str=CONF.NETWORK_MODE_STR,
        transit_mode_str=CONF.TRANSIT_MODE
    )

    planbuilder.create_plan(
        network_file_path=args["network_file"], 
        demand_file_path=args["demand_file"], 
        pickuppoint_file_path=args["pickuppoint_file"], route_file_path=args["route_file"], 
        vehicle_dict=CONF.TRANSIT_VEHICLE_TYPE_PROP_DICT, 
        start_time=CONF.TIME_TRANSIT_START, minute_between_start=CONF.TIME_BETWEEN_NEW_TRANSIT_RELEASE_MINUTE,
        max_roundtrip_minute=CONF.TIME_TRANSIT_RETURN_MINUTE, wait_minute_at_stop=CONF.TIME_WAITING_MIN
    )

    if args["matsim_data_output_dir"] is not None:
        planbuilder.write_plan_matsim_format(output_dir_path=args["matsim_data_output_dir"])
    
    if args["customsim_data_output_dir"] is not None:
        planbuilder.write_customsim_input(
            output_dir_path=args["customsim_data_output_dir"], 
            shelterid_list=[381, 382], 
            minute_between_start=CONF.TIME_BETWEEN_NEW_TRANSIT_RELEASE_MINUTE,
            separate_return_route=(not bool(args["same_return_route"]))
        )
