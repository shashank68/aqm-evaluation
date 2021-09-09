(TOTAL_LATENCY, LATENCY_UNIT) = (80, "ms")  # Total Round trip latency

# Client to router Bandwidth will be 10 * Bottleneck bandwidth
(BOTTLENECK_BANDWIDTH, BW_UNIT) = (80, "mbit")

AQM = "fq_pie"  # set at router egress interface
QDELAY_TARGET = "5ms"
ECN = False

TOTAL_NODES_PER_SIDE = 1  # Number of clients

DEBUG_LOGS = False
FLENT_TEST_NAME = "tcp_nup"  # e.g rrul, tcp_nup, cubic_reno, tcp_1up

TEST_DURATION = 200
STEP_SIZE = 0.05  # Resolution in seconds
UPLOAD_STREAMS = 1
RUNNER_DELAY = 0  # Delay before starting netperf etc..

OFFLOADS = True
OFFLOAD_TYPES = ["gso", "gro", "tso"]


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