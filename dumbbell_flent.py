import argparse
import glob
import gzip
import json
from logging import root
import os
import re
import shlex
import subprocess
import time
from multiprocessing import Process

from nest.engine.exec import exec_subprocess
from nest.topology import *

from exp_config import *

####### CONFIGURATION ###########

args_parser = argparse.ArgumentParser()
arg_parser_def(args_parser)
args = args_parser.parse_args()

AQM = args.qdisc or AQM
UPLOAD_STREAMS = args.number_of_tcp_flows or UPLOAD_STREAMS
BOTTLENECK_BANDWIDTH = args.bottleneck_bw or BOTTLENECK_BANDWIDTH
ROUTER1_BW_INT = args.router1_bw or ROUTER1_BW
ROUTER2_BW_INT = args.router2_bw or ROUTER2_BW
TOTAL_LATENCY = args.rtt or TOTAL_LATENCY
QDELAY_TARGET = args.qdelay_target or QDELAY_TARGET
TEST_DURATION = args.duration or TEST_DURATION
RESULTS_DIR = args.results_dir or RESULTS_DIR

if args.ecn:
    ECN = args.ecn == "Yes"
if args.no_offloads:
    OFFLOADS = args.no_offloads == "No"

title = f"{AQM}_{UPLOAD_STREAMS}_{ROUTER1_BW}up_{ROUTER2_BW}down_{TOTAL_LATENCY}_"
title += "ECN_" if ECN else ""
title += "OFFLD_" if OFFLOADS else ""

###############################

client_router_latency = 1.5
router_router_latency = 20

client_router_latency = f"{client_router_latency}{LATENCY_UNIT}"
router_router_latency = f"{router_router_latency}{LATENCY_UNIT}"

client_router_bandwidth = f"1000mbit"
ROUTER1_BW = f"{ROUTER1_BW_INT}{BW_UNIT}"
ROUTER2_BW = f"{ROUTER2_BW_INT}{BW_UNIT}"


# Assigning number of nodes on either sides of the dumbbell according to input
num_of_left_nodes = TOTAL_NODES_PER_SIDE
num_of_right_nodes = TOTAL_NODES_PER_SIDE

###### TOPOLOGY CREATION ######

# Creating the routers for the dumbbell topology
left_router = Node("left-router")
right_router = Node("right-router")

# Enabling IP forwarding for the routers
left_router.enable_ip_forwarding()
right_router.enable_ip_forwarding()

# Lists to store all the left and right nodes
left_nodes = []
right_nodes = []

# Creating all the left and right nodes
for i in range(num_of_left_nodes):
    left_nodes.append(Node("left-node-" + str(i)))

for i in range(num_of_right_nodes):
    right_nodes.append(Node("right-node-" + str(i)))

print("Nodes and routers created")

# Add connections

# Lists of tuples to store the interfaces connecting the router and nodes
left_node_connections = []
right_node_connections = []

# Connections of the left-nodes to the left-router
for i in range(num_of_left_nodes):
    left_node_connections.append(connect(left_nodes[i], left_router))

# Connections of the right-nodes to the right-router
for i in range(num_of_right_nodes):
    right_node_connections.append(connect(right_nodes[i], right_router))

# Connecting the two routers
(left_router_connection, right_router_connection) = connect(left_router, right_router)

print("Connections made")

###### ADDRESS ASSIGNMENT ######

# A subnet object to auto generate addresses in the same subnet
# This subnet is used for all the left-nodes and the left-router
left_subnet = Subnet("10.0.0.0/24")

for i in range(num_of_left_nodes):
    # Copying a left-node's interface and it's pair to temporary variables
    node_int = left_node_connections[i][0]
    router_int = left_node_connections[i][1]

    # Assigning addresses to the interfaces
    node_int.set_address(left_subnet.get_next_addr())
    router_int.set_address(left_subnet.get_next_addr())

# This subnet is used for all the right-nodes and the right-router
right_subnet = Subnet("10.0.1.0/24")

for i in range(num_of_right_nodes):
    # Copying a right-node's interface and it's pair to temporary variables
    node_int = right_node_connections[i][0]
    router_int = right_node_connections[i][1]

    # Assigning addresses to the interfaces
    node_int.set_address(right_subnet.get_next_addr())
    router_int.set_address(right_subnet.get_next_addr())

# This subnet is used for the connections between the two routers
router_subnet = Subnet("10.0.2.0/24")

# Assigning addresses to the connections between the two routers
left_router_connection.set_address(router_subnet.get_next_addr())
right_router_connection.set_address(router_subnet.get_next_addr())

print("Addresses are assigned")

####### ROUTING #######

# If any packet needs to be sent from any left-nodes, send it to left-router
for i in range(num_of_left_nodes):
    left_nodes[i].add_route("DEFAULT", left_node_connections[i][0])

# If the destination address for any packet in left-router is
# one of the left-nodes, forward the packet to that node
for i in range(num_of_left_nodes):
    left_router.add_route(
        left_node_connections[i][0].get_address(), left_node_connections[i][1]
    )

# If the destination address doesn't match any of the entries
# in the left-router's iptables forward the packet to right-router
left_router.add_route("DEFAULT", left_router_connection)

# If any packet needs to be sent from any right nodes, send it to right-router
for i in range(num_of_right_nodes):
    right_nodes[i].add_route("DEFAULT", right_node_connections[i][0])

# If the destination address for any packet in left-router is
# one of the left-nodes, forward the packet to that node
for i in range(num_of_right_nodes):
    right_router.add_route(
        right_node_connections[i][0].get_address(), right_node_connections[i][1]
    )

# If the destination address doesn't match any of the entries
# in the right-router's iptables forward the packet to left-router
right_router.add_route("DEFAULT", right_router_connection)

qdisc_kwargs = {}


if AQM == "cake":
    # configure cake parameters to run COBALT
    qdisc_kwargs["unlimited"] = ""
    qdisc_kwargs["raw"] = ""
    qdisc_kwargs["besteffort"] = ""
    qdisc_kwargs["no-ack-filter"] = ""
    qdisc_kwargs["rtt"] = f"{TOTAL_LATENCY}{LATENCY_UNIT}"
else:
    qdisc_kwargs["target"] = QDELAY_TARGET

    if ECN:
        qdisc_kwargs["ecn"] = ""


# Setting up the attributes of the connections between
# the nodes on the left-side and the left-router
for i in range(num_of_left_nodes):
    left_node_connections[i][0].set_attributes(
        client_router_bandwidth, client_router_latency
    )
    left_node_connections[i][1].set_attributes(
        client_router_bandwidth, client_router_latency
    )

# Setting up the attributes of the connections between
# the nodes on the right-side and the right-router
for i in range(num_of_right_nodes):
    right_node_connections[i][0].set_attributes(
        client_router_bandwidth, client_router_latency
    )
    right_node_connections[i][1].set_attributes(
        client_router_bandwidth, client_router_latency
    )

print("Setting Router connection attributes")
# Setting up the attributes of the connections between
# the two routers
left_router_connection.set_attributes(
    ROUTER1_BW, router_router_latency, AQM, **qdisc_kwargs
)
right_router_connection.set_attributes(
    ROUTER2_BW, router_router_latency, AQM, **qdisc_kwargs
)
oldpath = os. getcwd()
artifacts_dir = f"""{RESULTS_DIR}/{title}{time.strftime("%d-%m_%H:%M:%S.dump")}"""
os.makedirs(artifacts_dir, exist_ok=True)
os.chdir(artifacts_dir)
os.makedirs("up", exist_ok=True)
os.makedirs("down", exist_ok=True)
os.chdir(oldpath)

workers_list = []
tcpdump_processes = []
tcpdump_output_files = []

for i in range(TOTAL_NODES_PER_SIDE):
    cmd = f"ip netns exec {right_nodes[i].id} netserver &"
    exec_subprocess(cmd)

    cmd = f"ip netns exec {left_nodes[i].id} netserver &"
    exec_subprocess(cmd)

for i in range(TOTAL_NODES_PER_SIDE):
    src_node = left_nodes[i]
    dest_node = right_nodes[i]
    src_host_addr = left_node_connections[i][0].address.get_addr(with_subnet=False)
    dest_host_addr = right_node_connections[i][0].address.get_addr(with_subnet=False)

    if not OFFLOADS:
        left_node_connections[i][0].disable_offload(OFFLOAD_TYPES)
        right_node_connections[i][0].disable_offload(OFFLOAD_TYPES)

    if ECN:
        src_node.configure_tcp_param("ecn", 1)
        dest_node.configure_tcp_param("ecn", 1)

    ###  UPLOAD FLOW  ###
    cmd = (
        f"ip netns exec {src_node.id} flent {FLENT_TEST_NAME_1} "
        f" --test-parameter qdisc_stats_interfaces={left_router_connection.id}"
        f" --test-parameter qdisc_stats_hosts={left_router.id}"
        f" --test-parameter upload_streams={UPLOAD_STREAMS}"
        f" --output {artifacts_dir}/up/output.txt"
        f" --data-dir {artifacts_dir}/up"
        f" --length {TEST_DURATION}"
        f" --step-size {STEP_SIZE}"
        f" --host {dest_host_addr}"
        f" --delay {RUNNER_DELAY}"
        f" --title-extra {title}"
        " --socket-stats"
    )
    if DEBUG_LOGS:
        cmd += f" --log-file {artifacts_dir}/up/debug.log"

    workers_list.append(Process(target=exec_subprocess, args=(cmd,)))

    tcpdump_output_file = f"{artifacts_dir}/up/tcpdump.out"
    tcpdump_output_files.append(tcpdump_output_file)

    # run tcpdump on the right router to analyse packets and compute link utilization
    tcpdump_cmd = f"ip netns exec {dest_node.id} tcpdump -i {dest_node.interfaces[0].id} -evvv -tt -Q in"
    tcpdump_processes.append(
        subprocess.Popen(
            shlex.split(tcpdump_cmd),
            stdout=open(tcpdump_output_file, "w"),
            stderr=subprocess.DEVNULL,
        )
    )

    ###   DOWNLOAD FLOW  ###
    cmd = (
        f"ip netns exec {dest_node.id} flent {FLENT_TEST_NAME_1} "
        f" --test-parameter qdisc_stats_interfaces={right_router_connection.id}"
        f" --test-parameter qdisc_stats_hosts={right_router.id}"
        f" --test-parameter upload_streams={UPLOAD_STREAMS}"
        f" --output {artifacts_dir}/down/output.txt"
        f" --data-dir {artifacts_dir}/down"
        f" --length {TEST_DURATION}"
        f" --step-size {STEP_SIZE}"
        f" --host {src_host_addr}"
        f" --delay {RUNNER_DELAY}"
        f" --title-extra {title}"
        " --socket-stats"
    )
    if DEBUG_LOGS:
        cmd += f" --log-file {artifacts_dir}/down/debug.log"

    workers_list.append(Process(target=exec_subprocess, args=(cmd,)))

    tcpdump_output_file = f"{artifacts_dir}/down/tcpdump.out"
    tcpdump_output_files.append(tcpdump_output_file)

    # run tcpdump on the left router to analyse packets and compute link utilization
    tcpdump_cmd = f"ip netns exec {src_node.id} tcpdump -i {src_node.interfaces[0].id} -evvv -tt -Q in"
    tcpdump_processes.append(
        subprocess.Popen(
            shlex.split(tcpdump_cmd),
            stdout=open(tcpdump_output_file, "w"),
            stderr=subprocess.DEVNULL,
        )
    )

print("\n🤞 STARTED FLENT EXECUTION 🤞\n")
for worker in workers_list:
    worker.start()

for i in range(TOTAL_NODES_PER_SIDE):
    workers_list[i].join()
    # tcpdump_processes[i].terminate()

print("\n🎉 FINISHED FLENT EXECUTION 🎉\n")

####### LINK UTILISATION COMPUTATION #######
for tcpdump_output_file in tcpdump_output_files:
    packets = []
    f = open(tcpdump_output_file, "r")
    output = f.read()
    f.close()
    os.remove(tcpdump_output_file)

    # get the timestamp and packet size of each of the packets
    timestamps = list(map(float, re.findall(r"^\d*\.\d*", output, re.M)))
    packet_sizes = list(
        map(lambda x: int(x.split(" ")[1][:-1]),
            re.findall(r"length [\d]*:", output))
    )

    for i, pckt_size in enumerate(packet_sizes):
        packets.append((timestamps[i], pckt_size))

    curr_timestamp = packets[0][0]
    curr_packet_size_sum = packets[0][1]
    link_utilization_raw_values = []
    link_utilization_metadata = {
        "IDX": 7,
        "MAX_VALUE": 0,
        "MEAN_VALUE": 0,
        "MIN_VALUE": 101,
        "RUNNER": "PingRunner",
        "UNITS": "percent",
    }
    percent_sum = 0
    seq = 1.0

    bottleneck_bandwidth = ROUTER1_BW_INT
    if(os.path.basename(os.path.dirname(tcpdump_output_file)) == 'down'):
        bottleneck_bandwidth = ROUTER2_BW_INT

    for packet in packets:
        # if the packet belongs to a different bucket than the previous one, append
        # the stats to a new datapoint and create a new bucket
        if packet[0] - curr_timestamp > STEP_SIZE:
            link_utilization_percent = (
                curr_packet_size_sum
                * 8
                * 100
                / (int(bottleneck_bandwidth) * 1000000 * STEP_SIZE)
            )

            link_utilization_raw_values.append(
                {"seq": seq, "t": curr_timestamp, "val": link_utilization_percent}
            )
            link_utilization_metadata["MAX_VALUE"] = max(
                link_utilization_metadata["MAX_VALUE"], link_utilization_percent
            )
            link_utilization_metadata["MIN_VALUE"] = min(
                link_utilization_metadata["MIN_VALUE"], link_utilization_percent
            )

            percent_sum += link_utilization_percent
            curr_timestamp = packet[0]
            curr_packet_size_sum = packet[1]
            seq += 1.0

        # else add the stats to the current datapoint
        else:
            curr_packet_size_sum += packet[1]

    link_utilization_metadata["MEAN_VALUE"] = percent_sum / seq

    # Adding the raw values of link utilization into the gz file
    results_file = glob.glob(f"{os.path.dirname(tcpdump_output_file)}/*.gz")[0]
    results_file_content = ""

    # Firstly, decompress the content and get the json results
    with gzip.open(results_file, "rb") as f:
        results_file_content = json.loads(f.read())

    # Add the link utilization results into the dictionary
    results_file_content["raw_values"]["Link Utilization"] = link_utilization_raw_values
    results_file_content["metadata"]["SERIES_META"][
        "Link Utilization"
    ] = link_utilization_metadata

    # Alter the existing gz file to include the additional content
    with gzip.open(results_file, "wb") as f:
        f.write(json.dumps(results_file_content).encode("UTF-8"))

print("\n🎉 STARTING PLOT EXTRACTION 🎉\n")
root_dir = os.getcwd()
for subdir in ['up', 'down']:
    os.chdir(artifacts_dir + '/' + subdir)
    res_file = glob.glob("*.gz")[0]
    os.makedirs("plots", exist_ok=True)

    for plot_title in PLOT_TITLES:
        exec_subprocess(
            f"flent {res_file} --plot {plot_title} -o plots/{plot_title}.png")

    os.chdir(root_dir)

print("\n🎉 FINISHED PLOT EXTRACTION 🎉\n")

os.chown(artifacts_dir, int(os.getenv("SUDO_UID")), int(os.getenv("SUDO_GID")))
# os.chown(f"{artifacts_dir}/plots", int(os.getenv("SUDO_UID")), int(os.getenv("SUDO_GID")))
