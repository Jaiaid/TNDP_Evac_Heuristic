import sys
import copy
import os

INFINTE_STR_PLACEHOLDER = "-1"
INFINTE_FLOAT_PLACEHOLDER = float("inf")
LIMITING_DISTANCE = float("inf")

if __name__=="__main__":
    if len(sys.argv) != 3:
        print("python3 edge_contraction.py <network_filepath> <output_filepath>")
        exit()

    network_file_path = sys.argv[1]

    network_graph = []
    node_id_inout_degree_count_dict = {}
    # parse file and populate network graph

    # network file format is
    # first line : <node count>
    # each line : each row of matrix where each entry m_ij contains distance between node i and j
    # infinite distance or disconnection is indicated by INFINTE_STR_PLACEHOLDER
    with open(network_file_path) as net_file:
        lines = net_file.readlines()
        node_count=int(lines[0])

        for idx, line in enumerate(lines[1:]):
            number_strings=line.rsplit()
            assert node_count==len(number_strings), \
                "network row {0} has less entry (={1}) than node count (={2})".format(idx, len(number_strings), node_count)

            network_graph.append([])
            for number_string in number_strings:
                if number_string != INFINTE_STR_PLACEHOLDER:
                    network_graph[-1].append(float(number_string))
                else:
                    network_graph[-1].append(INFINTE_FLOAT_PLACEHOLDER)

            assert len(network_graph[-1])==node_count

        assert len(network_graph)==node_count

    uncontracted_graph_edge_count = 0
    contracted_edge_count = 0
    output_network_graph = copy.deepcopy(network_graph)
    # populate inout degree count
    # first init each node dict entry 
    # to avoid existance check at each entry of matrix
    for i in range(len(network_graph)):
        # each dict entry is a dict with two key "outnode" "innode"
        # each key has dict of to which node or from which node 
        # dict is chosen so letter deleting can be easier
        node_id_inout_degree_count_dict[i] = {"innode": {}, "outnode": {}}
    for i in range(len(network_graph)):
        for j in range(len(network_graph[i])):
            # to avoid self edge
            if network_graph[i][j] != INFINTE_FLOAT_PLACEHOLDER and network_graph[i][j] != 0:
                # value is not important, only the node id
                node_id_inout_degree_count_dict[i]["outnode"][j] = 0
                node_id_inout_degree_count_dict[j]["innode"][i] = 0
                uncontracted_graph_edge_count += 1
    # now find the node with out == 1, in == 1
    for node_id, degree_dict in node_id_inout_degree_count_dict.items():
        if len(degree_dict["outnode"]) == 1 and len(degree_dict["innode"]) == 1:
            parent_node = list(degree_dict["innode"].keys())[0]
            child_node = list(degree_dict["outnode"].keys())[0]
            # degree_dict["innode"].keys()[0] -> node_id -> degree_dict["outnode"].keys()[0]
            # these two edges will contract into one
            contracted_edge_count += 1
            # create connection between node_id parent and node_id's child
            if output_network_graph[parent_node][child_node] == INFINTE_FLOAT_PLACEHOLDER:
                output_network_graph[parent_node][child_node] = \
                    network_graph[parent_node][node_id] + network_graph[node_id][child_node]
            else:
                output_network_graph[parent_node][child_node] = \
                    min(network_graph[parent_node][node_id] + network_graph[node_id][child_node], network_graph[parent_node][child_node])

            # disconnect node_id
            output_network_graph[parent_node][node_id] = INFINTE_FLOAT_PLACEHOLDER
            output_network_graph[node_id][child_node] = INFINTE_FLOAT_PLACEHOLDER

            # remove node_of from dict of parent and child
            del node_id_inout_degree_count_dict[parent_node]["outnode"][node_id]
            del node_id_inout_degree_count_dict[child_node]["innode"][node_id]


    print("uncontracted graph edge count {0}".format(uncontracted_graph_edge_count))
    print("after contraction, edge count {0}".format(uncontracted_graph_edge_count - contracted_edge_count))
    # dump the output network to file
    # output network file format is
    # first line : <node count>
    # each line : each row of matrix where each entry m_ij contains distance between node i and j
    # infinite distance or disconnection is indicated by INFINTE_STR_PLACEHOLDER
    with open(sys.argv[2], mode="w") as fout:
        fout.write(str(len(output_network_graph)) + os.linesep)
        for i in range(len(output_network_graph)):
            line = ""
            for j in range(len(output_network_graph[i])):
                if output_network_graph[i][j] == INFINTE_FLOAT_PLACEHOLDER:
                    line += INFINTE_STR_PLACEHOLDER + " "
                else:
                    line += str(output_network_graph[i][j]) + " "
            fout.write(line + os.linesep)
