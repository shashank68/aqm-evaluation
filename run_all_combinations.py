# Run dumbell_flent.py script with different configurations

import itertools
import os
import time
from multiprocessing import Process

from nest.engine.exec import exec_subprocess
from tqdm import tqdm

# Number of parallel processes to run
NUM_PROCS = 3

# QDISCS = ["fq_codel", "fq_pie", "cake"]
# FLOWS = [1, 3, 16]
# BOTTLENECK_BANDWIDTHS = [80, 160, 1000]
# RTTS = [4, 40, 80, 800]
# ECN = ["No", "Yes"]
# OFFLOADS = ["No", "Yes"]

QDISCS = ["fq_codel"]
FLOWS = [1]
BOTTLENECK_BANDWIDTHS = [80, 160, 1000]
RTTS = [4]
ECN = ["No"]
OFFLOADS = ["No"]

params_combinations = itertools.product(
    QDISCS, FLOWS, BOTTLENECK_BANDWIDTHS, RTTS, ECN, OFFLOADS
)

all_cmds = []

for combination in params_combinations:
    all_cmds.append(
        "python ../dumbell_flent.py"
        " --qdisc {}"
        " --number_of_tcp_flows {}"
        " --bottleneck_bw {}"
        " --rtt {}"
        " --ecn {}"
        " --no_offloads {}".format(*combination)
    )

dir_name = time.strftime("ALL_COMBO_%d-%m_%H:%M:%S.dump")
os.mkdir(dir_name)
os.chdir(dir_name)

num_iterations = len(all_cmds) // NUM_PROCS
rem = len(all_cmds) % NUM_PROCS

for i in tqdm(range(0, num_iterations)):
    procs = [
        Process(target=exec_subprocess, args=(cmd,))
        for cmd in all_cmds[i * NUM_PROCS : (i + 1) * NUM_PROCS]
    ]
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join()

for i in range(rem):
    exec_subprocess(all_cmds[-(i + 1)])

os.chown(f"../{dir_name}", int(os.getenv("SUDO_UID")), int(os.getenv("SUDO_GID")))
