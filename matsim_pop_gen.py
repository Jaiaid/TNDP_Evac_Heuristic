import sys

NETWORK_NAME="halifax evacuation"

POP_TAG=["<population>", "</population>"]
AGENT_TAG=["<person id=\"{0}\">", "</person>"]
AGENT_PLAN_TAG=["<plan>", "</plan>"]
AGENT_ACT_DESC_TAG=["<act type=\"{0}\" x=\"{1}\" y=\"{2}\" />"]
AGENT_LEG_DESC_TAG=["<leg mode=\"{0}\" />"]

TYPE_STR="home"
LEG_MODE_STR="pt" 

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

                x_src = i*10
                y_src = (i//20) * 100
                x_dest = j*10
                y_dest = (j//20) * 100

                for k in range(person_count):
                    file_stream.write(AGENT_TAG[0].format(id_no)+'\n')
                    file_stream.write(AGENT_PLAN_TAG[0]+'\n')
                    write_act_desc(file_stream, TYPE_STR, x_src, y_src)
                    write_leg_desc(file_stream, LEG_MODE_STR)
                    write_act_desc(file_stream, TYPE_STR, x_dest, y_dest)
                    file_stream.write(AGENT_PLAN_TAG[1]+'\n')
                    file_stream.write(AGENT_TAG[1]+'\n')
                    id_no += 1


def write_act_desc(file_stream, type_str, x, y):
    file_stream.write(AGENT_ACT_DESC_TAG[0].format(type_str, x, y)+'\n')


def write_leg_desc(file_stream, mode_str):
    file_stream.write(AGENT_LEG_DESC_TAG[0].format(mode_str)+'\n')


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 main.py demand_file out_path")
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

    
    create_pop_file(demand_graph, sys.argv[2])

