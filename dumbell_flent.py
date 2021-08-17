import os
import subprocess
import time
from multiprocessing import Process

from nest.engine.exec import exec_subprocess
from nest.experiment import *
from nest.topology import *

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

TOTAL_LATENCY = 4  # Total Round trip latency

BOTTLENECK_BANDWIDTH = 1  # Client to router Bandwidth will be 10 * Bottleneck bandwidth
BW_UNIT = "gbit"

AQM = "fq_codel"  # set Router egress interface

ECN = False

TOTAL_NODES_PER_SIDE = 1  # Number of clients

DEBUG_LOGS = True
FLENT_TEST_NAME = "tcp_nup"  # e.g rrul, tcp_nup

TEST_DURATION = 30
STEP_SIZE = 0.05 # Resolution in seconds
UPLOAD_STREAMS = 1

OFFLOADS = True  # GSO, GRO
NIC_BUFFER = ""  # TX

###############################

client_router_latency = TOTAL_LATENCY / 8
router_router_latency = TOTAL_LATENCY / 4

client_router_latency = str(client_router_latency) + "ms"
router_router_latency = str(router_router_latency) + "ms"


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


# Setting up the attributes of the connections between
# the two routers
left_router_connection.set_attributes(
    bottleneck_bandwidth, router_router_latency, AQM, **qdisc_kwargs
)
right_router_connection.set_attributes(
    bottleneck_bandwidth, router_router_latency, AQM, **qdisc_kwargs
)

title = "ECN_" if ECN else ""
title += AQM
artifacts_dir = title + FLENT_TEST_NAME + time.strftime("%d-%m_%H:%M:%S.dump")
os.mkdir(artifacts_dir)
workers_list = []

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
        --length {TEST_DURATION} \
        --host {right_node_connections[i][0].address.get_addr(with_subnet=False)} \
        --output {node_dir}/output.txt \
        --data-dir {node_dir} \
        --title-extra {title} 
        """

    if DEBUG_LOGS:
        cmd += f"--log-file {node_dir}/debug.log"

    workers_list.append(Process(target=exec_subprocess, args=(cmd,)))

for worker in workers_list:
    worker.start()

for worker in workers_list:
    worker.join()

print("\n🎉 FINISHED EXECUTION 🎉\n")
