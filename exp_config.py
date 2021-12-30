(TOTAL_LATENCY, LATENCY_UNIT) = (724, "ms")  # Total Round trip latency

ROUTER_ROUTER_LATENCY = 350  # Total / 2 (approx)
CLIENT_ROUTER_LATENCY = 6

# Client to router Bandwidth will be 10 * Bottleneck bandwidth

(BOTTLENECK_BANDWIDTH, BW_UNIT) = ("80", "mbit")
ROUTER1_BW = 3
ROUTER2_BW = 20

AQM = "fq_pie"  # set at router egress interface
QDELAY_TARGET = "40ms"
AQM_INTERVAL = "724ms"
ECN = True

TOTAL_NODES_PER_SIDE = 1  # Number of clients

DEBUG_LOGS = True
FLENT_TEST_NAME = "tcp_nup"  # e.g rrul, tcp_nup, cubic_reno, tcp_1up

TEST_DURATION = 30
STEP_SIZE = 0.5  # Resolution in seconds
UPLOAD_STREAMS = 20
RUNNER_DELAY = 0  # Delay before starting netperf etc..

OFFLOADS = True
OFFLOAD_TYPES = ["gso", "gro", "tso"]

RESULTS_DIR = "."

PLOT_TITLES = [
    "upload",
    "ping_smooth",
    "tcp_cwnd",
    "link_utilization",
    "backlog",
]


def arg_parser_def(parser):
    parser.add_argument("--rtt", type=int, help="Round trip time for flows (ms)")
    parser.add_argument("--ecn", type=str, help="Turn on ECN", choices=["Yes", "No"])
    parser.add_argument(
        "--duration", type=int, help="Duration of test in seconds", metavar="TIME"
    )
    parser.add_argument(
        "--bottleneck_bw",
        type=int,
        help="Bottleneck bandwidth (mbit)",
        metavar="BANDWIDTH",
    )
    parser.add_argument(
        "--router1_bw",
        type=int,
        help="Bottleneck Bandwidth at the router1 interface (mbit)",
        metavar="BANDWIDTH",
    )
    parser.add_argument(
        "--router2_bw",
        type=int,
        help="Bottleneck Bandwidth at the router2 interface (mbit)",
        metavar="BANDWIDTH",
    )
    parser.add_argument(
        "--qdisc",
        type=str,
        help="AQM algorithm (qdisc)",
        choices=["fq_codel", "fq_pie", "codel", "pie", "cake"],
    )
    parser.add_argument(
        "--no_offloads",
        type=str,
        help="Turn off GSO, GRO offloads",
        choices=["Yes", "No"],
    )
    parser.add_argument(
        "--number_of_tcp_flows",
        type=int,
        help="Number of flows in tcp_nup flent test",
        metavar="NUM",
    )
    parser.add_argument(
        "--qdelay_target",
        type=int,
        help="Queue delay target (For qdisc)",
        metavar="TARGET",
    )
    parser.add_argument(
        "--results_dir",
        type=str,
        help="Directory to store the results",
        metavar="DIR",
    )
