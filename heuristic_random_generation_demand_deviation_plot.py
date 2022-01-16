import matplotlib.pyplot as plot
import re

INPUT_FILEPATH = "route_balance_quality_random_compare_data_after_node_select_logic_change.txt"

if __name__=="__main__":
    REGEX_HOPCOUNT_LINE = r"^Max hop count : (\d+)"
    REGEX_HEU_DEVIATION_LINE = r"^heuristic deviation : (\d*\.\d+)"
    REGEX_RANDOM_DEVIATION_LINE = r"^random route generation deviation : (\d*\.\d+)"
    
    x = []
    yheu = []
    yrandom = []

    with open(INPUT_FILEPATH) as fin:
        for line in fin.readlines():
            result = re.search(REGEX_HOPCOUNT_LINE, line)
            if result is not None:
                x.append(int(result.groups()[0]))
                continue
            result = re.search(REGEX_HEU_DEVIATION_LINE, line)
            if result is not None:
                yheu.append(float(result.groups()[0]))
                continue
            result = re.search(REGEX_RANDOM_DEVIATION_LINE, line)
            if result is not None:
                yrandom.append(float(result.groups()[0]))
                continue    

    fig, ax = plot.subplots()

    ax.set_title("Route Demand Std. Deviation")
    
    ax.plot(x, yheu, label="heu soloution")
    ax.plot(x, yrandom, label="random solution")

    ax.legend()
    ax.set_xlabel("max pickup point")
    ax.set_ylabel("route demand std. deviation")
    #ax_evac.xaxis.set_tick_params(labelsize="4")

    fig.savefig("heuristic_vs_random_generation_routedemand_stddeviation_compare.png", dpi=300)
