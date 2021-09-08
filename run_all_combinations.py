# Run dumbell_flent.py script with different configurations

import itertools
import os
import time

from nest.engine.exec import exec_subprocess
from tqdm import tqdm

QDISCS = ["fq_codel", "fq_pie", "cake"]
FLOWS = [1, 3, 16]
BOTTLENECK_BANDWIDTHS = [80, 160, 1000]
RTTS = [4, 40, 80, 800]
ECN = ["No", "Yes"]
OFFLOADS = ["No", "Yes"]

# QDISCS = ["fq_codel", "fq_pie"]
# FLOWS = [1]
# BOTTLENECK_BANDWIDTHS = [160, 1000]
# RTTS = [4]
# ECN = ["No"]
# OFFLOADS = ["No"]

params_combinations = itertools.product(
    QDISCS, FLOWS, BOTTLENECK_BANDWIDTHS, RTTS, ECN, OFFLOADS
)

all_cmds = []

for combination in params_combinations:
    all_cmds.append(
        """python \
        ../dumbell_flent.py \
        --qdisc {} \
        --number_of_tcp_flows {} \
        --bottleneck_bw {} \
        --rtt {} \
        --ecn {} \
        --no_offloads {} \
        """.format(
            *combination
        )
    )

dir_name = time.strftime("ALL_COMBO_%d-%m_%H:%M:%S.dump")
os.mkdir(dir_name)
os.chdir(dir_name)

for cmd in tqdm(all_cmds):
    exec_subprocess(cmd)
