import sys

NETWORK_NAME="halifax evacuation"

ROOT_TAG=[
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
</vehicleType>"
]

TRANSIT_VEHICLE_TAG=["<vehicle id=\"{0}\" type=\"{1}\"/>"]

TOTAL_BUS = 300
TRANSIT_VEHICLE_TYPE_PROP_DICT = \
{
    "bus": {"count": TOTAL_BUS, "seat": 40, "standing": 10, "length": 8}
}


def create_vehicle_file(file_name):
    with open(file_name, "w") as fout:
        fout.write(ROOT_TAG[0]+"\n")

        for idx, vehicle_name in enumerate(TRANSIT_VEHICLE_TYPE_PROP_DICT):
            prop = TRANSIT_VEHICLE_TYPE_PROP_DICT[vehicle_name]
            write_vehicle_desc(fout, idx, vehicle_name, prop["seat"], prop["standing"], prop["length"])

            for num in range(prop["count"]):
                write_pervehicle_entry(fout, vehicle_name+"_{0}".format(num), idx)

        fout.write(ROOT_TAG[1]+"\n")


def write_vehicle_desc(file_stream, type_id, name, seat, standing_cap, length):
    file_stream.write(TRANSIT_DESC_TAG[0].format(type_id, name, seat, standing_cap, length)+'\n')


def write_pervehicle_entry(file_stream, id_no, type_no):
    file_stream.write(TRANSIT_VEHICLE_TAG[0].format(id_no, type_no)+'\n')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 main.py output_path")
        exit(0)
    
    create_vehicle_file(sys.argv[1])

