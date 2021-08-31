import os
import subprocess
import time
from multiprocessing import Process
from shutil import copy2
import matplotlib.pyplot as plt
import re

from nest.engine.exec import exec_subprocess
from nest.topology import *
import argparse

##############################
# Topology: Dumbbell
#
#   ln0----------------                      ---------------rn0
#                      \                    /
#   ln1---------------  \                  /  ---------------rn1
#                      \ \                / /
#   ln2---------------- lr ------------- rr ---------------- rn2
#   .                  /                    \                .
#   .                 /                      \               .
#   .                /                        \              .
#   .               /                          \             .
#   ln6------------                              ------------rn6
#
##############################


####### CONFIGURATION ###########

(TOTAL_LATENCY, LAT_UNIT) = (4, "ms")  # Total Round trip latency

BOTTLENECK_BANDWIDTH, BW_UNIT = (80, "mbit")  # Client to router Bandwidth will be 10 * Bottleneck bandwidth

AQM = "fq_pie"  # set at router egress interface

ECN = True

SET_TARGET = False

TOTAL_NODES_PER_SIDE = 1  # Number of clients

DEBUG_LOGS = True
FLENT_TEST_NAME = "tcp_nup"  # e.g rrul, tcp_nup, cubic_reno, tcp_1up
TCP_CONG_CONTROL = "cubic"

TEST_DURATION = 30
STEP_SIZE = 0.05  # Resolution in seconds
UPLOAD_STREAMS = 1

OFFLOADS = True  # GSO, GRO
NIC_BUFFER = ""  # TX

# Adding CL arguments functionality
# If no arguments are added then the ones in this script are used
parser = argparse.ArgumentParser()
parser.add_argument("--rtt", type=int, help="Enter the RTT")
parser.add_argument("--bottleneck_bw", type=int, help="Enter the bottleneck bandwidth")
parser.add_argument("--AQM", type=str, help="Enter the AQM algorithm")
parser.add_argument("--cong_control_algo", type=str, help="Enter the congestion control algorithm")
parser.add_argument("--ecn", type=str, help="Set the ecn flag")
parser.add_argument("--offloads", type=str, help="Set the offloads flag")
parser.add_argument("--number_of_flows", type=int, help="Set the number of flows")
parser.add_argument("--target", type=int, help="Set the target")

args = parser.parse_args()

if args.rtt is not None:
    TOTAL_LATENCY = args.rtt

if args.bottleneck_bw is not None:
    BOTTLENECK_BANDWIDTH = args.bottleneck_bw

if args.AQM is not None:
    AQM = args.AQM

if args.cong_control_algo is not None:
    TCP_CONG_CONTROL = args.cong_control_algo

if args.ecn is not None:
    ECN = True if args.ecn == "Yes" else False

if args.offloads is not None:
    OFFLOADS = True if args.offloads == "Yes" else False

if args.number_of_flows is not None:
    TOTAL_NODES_PER_SIDE = args.number_of_flows

if args.target is not None:
    SET_TARGET = True
    TARGET = args.target

title = str(TOTAL_NODES_PER_SIDE) + "_"
title += "ECN_" if ECN else ""
title += "OFL_" if OFFLOADS else ""
title += AQM + "_" + str(BOTTLENECK_BANDWIDTH) + BW_UNIT + '_' + str(TOTAL_LATENCY) + LAT_UNIT + '_' + TCP_CONG_CONTROL + "_"
###############################

client_router_latency = TOTAL_LATENCY / 8
router_router_latency = TOTAL_LATENCY / 4

client_router_latency = str(client_router_latency) + LAT_UNIT
router_router_latency = str(router_router_latency) + LAT_UNIT


client_router_bandwidth = str(BOTTLENECK_BANDWIDTH * 10) + BW_UNIT
bottleneck_bandwidth = str(BOTTLENECK_BANDWIDTH) + BW_UNIT

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

if ECN:
    qdisc_kwargs = {"ecn": ""}

if SET_TARGET:
    qdisc_kwargs["target"] = f"{TARGET}ms"

# Setting up the attributes of the connections between
# the nodes on the left-side and the left-router
for i in range(num_of_left_nodes):
    left_node_connections[i][0].set_attributes(
        client_router_bandwidth, client_router_latency, **qdisc_kwargs
    )
    left_node_connections[i][1].set_attributes(
        client_router_bandwidth, client_router_latency, **qdisc_kwargs
    )

# Setting up the attributes of the connections between
# the nodes on the right-side and the right-router
for i in range(num_of_right_nodes):
    right_node_connections[i][0].set_attributes(
        client_router_bandwidth, client_router_latency, **qdisc_kwargs
    )
    right_node_connections[i][1].set_attributes(
        client_router_bandwidth, client_router_latency, **qdisc_kwargs
    )

print("Setting Router connection attributes")
# Setting up the attributes of the connections between
# the two routers
left_router_connection.set_attributes(
    bottleneck_bandwidth, router_router_latency, AQM, **qdisc_kwargs
)
right_router_connection.set_attributes(
    bottleneck_bandwidth, router_router_latency, AQM, **qdisc_kwargs
)

artifacts_dir = title + time.strftime("%d-%m_%H:%M:%S.dump")
os.mkdir(artifacts_dir)
copy2(os.path.abspath(__file__), artifacts_dir)

workers_list = []
tcpdump_processes = []
tcpdump_output_files = []

for i in range(TOTAL_NODES_PER_SIDE):
    cmd = f"ip netns exec {right_nodes[i].id} netserver"
    exec_subprocess(cmd)

for i in range(TOTAL_NODES_PER_SIDE):
    src_node = left_nodes[i]
    dest_node = right_nodes[i]

    if not OFFLOADS:
        exec_subprocess(
            f"ip netns e {src_node.id} eththool --offloads {src_node.interfaces[0].id} gro off"
        )
        exec_subprocess(
            f"ip netns e {src_node.id} eththool --offloads {src_node.interfaces[0].id} gso off"
        )

    if NIC_BUFFER:
        exec_subprocess(
            f"ip netns e {src_node.id} eththool --set-ring {src_node.interfaces[0].id} tx {NIC_BUFFER}"
        )

    if ECN:
        src_node.configure_tcp_param("ecn", 1)
        dest_node.configure_tcp_param("ecn", 1)

    node_dir = f"{artifacts_dir}/{src_node.name}"
    os.mkdir(node_dir)

    tcpdump_output_file = f"{node_dir}/tcpdump.out"
    tcpdump_output_files.append(tcpdump_output_file)

    # listen to the router qdisc stats only if it is the first client
    if i == 0:
        cmd = f"""
        ip netns exec {src_node.id} flent {FLENT_TEST_NAME} \
        --test-parameter qdisc_stats_hosts={left_router.id} \
        --test-parameter qdisc_stats_interfaces={left_router_connection.ifb.id} \
        """
    else:
        cmd = f"""
        ip netns exec {src_node.id} flent {FLENT_TEST_NAME} \
        """

    cmd += f"""
        --socket-stats \
        --step-size={STEP_SIZE} \
        --test-parameter upload_streams={UPLOAD_STREAMS} \
        --test-parameter tcp_cong_control={TCP_CONG_CONTROL} \
        --length {TEST_DURATION} \
        --host {right_node_connections[i][0].address.get_addr(with_subnet=False)} \
        --output {node_dir}/output.txt \
        --data-dir {node_dir} \
        --title-extra {title} 
        """

    if DEBUG_LOGS:
        cmd += f"--log-file {node_dir}/debug.log"

    workers_list.append(Process(target=exec_subprocess, args=(cmd,)))

    # run tcpdump on all the right nodes to analyse packets and compute link utilization
    # the output is stored in different files for different nodes
    tcpdump_processes.append(subprocess.Popen(
        f"""ip netns exec {dest_node.id} tcpdump -i {dest_node.interfaces[0].id} -evvv -tt""",
        stdout=open(tcpdump_output_file, "w"), stderr=subprocess.DEVNULL, shell=True))

print("\n🤞 STARTED FLENT EXECUTION 🤞\n")

for worker in workers_list:
    worker.start()

for i in range(TOTAL_NODES_PER_SIDE):
    workers_list[i].join()
    tcpdump_processes[i].terminate()

print("\n🎉 FINISHED FLENT EXECUTION 🎉\n")


####### LINK UTILISATION COMPUTATION #######

packets = []
for tcpdump_output_file in tcpdump_output_files:
    f = open(tcpdump_output_file, "r")
    output = f.read()

    # get the timestamp and packet size of each of the packets
    timestamps = list(
        map(lambda x: float(x), re.findall("^\d*\.\d*", output, re.M)))
    packet_sizes = list(
        map(lambda x: int(x.split(" ")[1][:-1]), re.findall("length [\d]*:", output)))

    for i in range(len(timestamps)):
        packets.append((timestamps[i], packet_sizes[i]))

# sort the packets received by different nodes according to the timestamp
packets.sort()

curr_timestamp = packets[0][0]
curr_packet_size_sum = packets[0][1]
time_datapoints = []
curr_time_datapoint = 0
throughput_datapoints = []

for packet in packets:
    # if the packet belongs to a different bucket than the previous one, append
    # the stats to a new datapoint and create a new bucket
    if(packet[0]-curr_timestamp > STEP_SIZE):
        time_datapoints.append(curr_time_datapoint)
        throughput_datapoints.append(
            curr_packet_size_sum*8*100/(BOTTLENECK_BANDWIDTH*1000000*STEP_SIZE))
        curr_timestamp = packet[0]
        curr_packet_size_sum = packet[1]
        curr_time_datapoint += STEP_SIZE

    # else add the stats to the current datapoint
    else:
        curr_packet_size_sum += packet[1]

time_datapoints.append(curr_time_datapoint)
throughput_datapoints.append(
    curr_packet_size_sum*8*100/(BOTTLENECK_BANDWIDTH*1000000*STEP_SIZE))

# Plot the points on a graph and save the graph as an image
plt.xlabel("Time (seconds)")
plt.ylabel("Link Utilization (Percentage)")
plt.plot(time_datapoints, throughput_datapoints)
plt.savefig(f"{artifacts_dir}/link_utilization.png")
