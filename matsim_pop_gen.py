import sys

NETWORK_NAME="halifax evacuation"

POP_TAG=[
"<?xml version=\"1.0\" ?>\n\
<!DOCTYPE plans SYSTEM \"http://www.matsim.org/files/dtd/plans_v4.dtd\">\n\
<plans>", 
"</plans>"
]
AGENT_TAG=["<person id=\"{0}\">", "</person>"]
AGENT_PLAN_TAG=["<plan>", "</plan>"]
AGENT_ACT_DESC_TAG=["<act type=\"{0}\" x=\"{1}\" y=\"{2}\" />"]
AGENT_LEG_DESC_TAG=["<leg mode=\"{0}\" />"]

TYPE_STR1="home"
TYPE_STR2="shelter"
TYPE_STR3="pt_interaction"

LEG_MODE_PT_STR="pt"
LEG_MODE_WALK_STR="transit_walk"

pickuppoint_list = []
nearest_stop_dict = {}
node_coordinate_dict = {}


def create_pop_file(demand_graph, file_name):
    with open(file_name, "w") as fout:
        fout.write(POP_TAG[0]+"\n")
        write_persons_tag(fout, demand_graph)        
        fout.write(POP_TAG[1]+"\n")


def write_persons_tag(file_stream, demand_graph):
    id_no = 0    
    for i in range(len(demand_graph)):
        for j in range(len(demand_graph)):
            if demand_graph[i][j] > 0:
                person_count = int(demand_graph[i][j])

                for k in range(person_count):
                    file_stream.write(AGENT_TAG[0].format(id_no)+'\n')
                    file_stream.write(AGENT_PLAN_TAG[0]+'\n')
                    write_act_desc(file_stream, TYPE_STR1, node_coordinate_dict[i][0], node_coordinate_dict[i][1])
                    #write_leg_desc(file_stream, LEG_MODE_WALK_STR)
                    write_act_desc(file_stream, TYPE_STR3, 
                        node_coordinate_dict[nearest_stop_dict[i]][0], 
                        node_coordinate_dict[nearest_stop_dict[i]][1])
                    write_leg_desc(file_stream, LEG_MODE_PT_STR)
                    write_act_desc(file_stream, TYPE_STR3, node_coordinate_dict[j][0], node_coordinate_dict[j][1])
                    write_leg_desc(file_stream, LEG_MODE_WALK_STR)
                    write_act_desc(file_stream, TYPE_STR2, node_coordinate_dict[j][0], node_coordinate_dict[j][1])
                    file_stream.write(AGENT_PLAN_TAG[1]+'\n')
                    file_stream.write(AGENT_TAG[1]+'\n')
                    id_no += 1


def write_act_desc(file_stream, type_str, x, y):
    file_stream.write(AGENT_ACT_DESC_TAG[0].format(type_str, x, y)+'\n')


def write_leg_desc(file_stream, mode_str):
    file_stream.write(AGENT_LEG_DESC_TAG[0].format(mode_str)+'\n')


def create_pickuppoint_list(pickup_point_file_path):
    with open(pickup_point_file_path) as net_file:
        lines = net_file.readlines()
        
        for idx, line in enumerate(lines):
            pickuppoint_list.append(int(line.rsplit()[0]))


def calc_euclid_dist(coord1, coord2):
    return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)**0.5 


def create_nearest_stop_dict(node_count):
    for i in range(node_count):
        x = i*10
        y = (i//20) * 100
        node_coordinate_dict[i] = (x, y)

    for i in range(node_count):
        mindist = float("inf")
        nearest_stop = None
        for stop_id in pickuppoint_list:
            dist = calc_euclid_dist(node_coordinate_dict[i], node_coordinate_dict[stop_id])
            if dist < mindist:
                nearest_stop = stop_id
                mindist = dist
        assert nearest_stop is not None
        nearest_stop_dict[i] = nearest_stop 


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 main.py demand_file pickuppoint_file out_path")
        exit(0)

    node_count = 0
    demand_graph = []
    with open(sys.argv[1]) as net_file:
        lines = net_file.readlines()
        node_count=int(lines[0])

        for idx, line in enumerate(lines[1:]):
            number_strings=line.rsplit()
            assert node_count==len(number_strings), "row {0} has less entry (={1}) than node count (={2})".format(idx, len(number_strings), node_count)

            demand_graph.append([])
            for number_string in number_strings:
                demand_graph[-1].append(float(number_string))

            assert len(demand_graph[-1])==node_count

        assert len(demand_graph)==node_count

    create_pickuppoint_list(sys.argv[2])
    create_nearest_stop_dict(node_count)
    create_pop_file(demand_graph, sys.argv[3])

