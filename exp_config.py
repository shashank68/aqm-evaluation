(TOTAL_LATENCY, LATENCY_UNIT) = (80, "ms")  # Total Round trip latency

# Client to router Bandwidth will be 10 * Bottleneck bandwidth
(router_1_bw, BW_UNIT_1) = (80, "mbit")
(router_2_bw, BW_UNIT_2) = (150, "mbit")

AQM = "fq_codel"  # set at router egress interface
QDELAY_TARGET = "5ms"
ECN = False

TOTAL_NODES_PER_SIDE = 1  # Number of clients

DEBUG_LOGS = True
FLENT_TEST_NAME_1 = "tcp_nup"  # e.g rrul, tcp_nup, cubic_reno, tcp_1up
FLENT_TEST_NAME_2 = "tcp_nup"

TEST_DURATION = 5
STEP_SIZE = 0.05  # Resolution in seconds
UPLOAD_STREAMS = 1
RUNNER_DELAY = 0  # Delay before starting netperf etc..

OFFLOADS = True
OFFLOAD_TYPES = ["gso", "gro", "tso"]

RESULTS_DIR = "."

PLOT_TITLES = [
    "totals",
    "upload",
    "upload_box",
    "upload_with_ping",
    "upload_with_ping_and_tcp_rtt",
    "tcp_delivery_with_ping",
    "tcp_delivery_with_rtt",
    "upload_scaled",
    "ping",
    "ping_smooth",
    "ping_cdf",
    "box_totals",
    "box_totals_combine",
    "box_ping_combine",
    "box_combine",
    "bar_combine",
    "tcp_cwnd",
    "tcp_rtt",
    "tcp_rtt_cdf",
    "tcp_rtt_box_combine",
    "tcp_rtt_bar_combine",
    "tcp_pacing",
    "link_utilization",
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
