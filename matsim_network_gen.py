import sys
import sim_conf as CONF

NETWORK_NAME="halifax evacuation"

NETWORK_TAG=[
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


def create_network_file(network_graph, file_name):
    with open(file_name, "w") as fout:
        fout.write(NETWORK_TAG[0].format(NETWORK_NAME)+"\n")
        write_nodes_tag(fout, network_graph)        
        write_links_tag(fout, network_graph)
        fout.write(NETWORK_TAG[1]+"\n")


def write_nodes_tag(file_stream, network_graph):
    file_stream.write(NODE_TAG[0]+'\n')
    for i in range(len(network_graph)):
        x = i*10
        y = (i//20) * 100

        write_node_desc(file_stream, i, x, y)
    file_stream.write(NODE_TAG[1]+'\n')


def write_node_desc(file_stream, id_no, x, y):
    file_stream.write(NODE_DESCRIPTION_TAG[0].format(id_no, x, y)+'\n')


def write_links_tag(file_stream, network_graph):
    id_no = 0
    file_stream.write(LINK_TAG[0]+'\n')
    for i in range(len(network_graph)):
        for j in range(len(network_graph[i])):
            if network_graph[i][j] > 0:
                write_link_desc(file_stream, id_no, i, j, network_graph[i][j], CONF.NETWORK_LANE_CAPACITY, CONF.NETWORK_MAX_LINK_SPEED, CONF.NETWORK_ROAD_LANE_COUNT, CONF.NETWORK_MODE_STR)
                id_no += 1
    file_stream.write(LINK_TAG[1]+'\n')


def write_link_desc(file_stream, id_no, src_id, dest_id, length, cap, speed, lane_count, mode_str):
    file_stream.write(LINK_DESCRIPTION_TAG[0].format(id_no, src_id, dest_id, length, cap, speed, lane_count, mode_str)+'\n')


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 main.py distance_file out_path")
        exit(0)

    node_count = 0
    network_graph = []
    with open(sys.argv[1]) as net_file:
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

    
    create_network_file(network_graph, sys.argv[2])

