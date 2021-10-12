"""Run dumbbell_flent.py script with different configurations"""

import itertools
import json
import os
import time
from multiprocessing import Process

from nest.engine.exec import exec_subprocess
from tqdm import tqdm

# Number of parallel processes to run
NUM_PROCESSES = 2

QDISCS = ["fq_codel", "fq_pie", "cake"]
FLOWS = [1, 3, 16]
BOTTLENECK_BANDWIDTHS = [80, 160, 1000]
RTTS = [4, 40, 80, 800]
ECN = ["No", "Yes"]
OFFLOADS = ["No", "Yes"]
DURATIONS = [200]
RESULTS_DIR = "."

try:
    with open("combinations_config.json", "r") as json_file:
        config = json.load(json_file)
    for key, val in config.items():
        print(key, val)
        if val:
            if isinstance(val, list):
                globals()[key] = val
except FileNotFoundError:
    print(
        "Copy combinations_config.json.example to combinations_config.json"
        " to use custom combinations.\n"
        "Running tests with default combinations\n"
    )


params_combinations = itertools.product(
    QDISCS, FLOWS, BOTTLENECK_BANDWIDTHS, RTTS, ECN, OFFLOADS, DURATIONS
)

all_cmds = []

for combination in params_combinations:
    RESULTS_DIR = "AQM={}/Flows={}/Bandwidth={}/RTT={}/ECN={}/Offloads={}".format(
        *combination
    )
    all_cmds.append(
        "python ../dumbbell_flent.py"
        " --qdisc {}"
        " --number_of_tcp_flows {}"
        " --rtt {}"
        " --ecn {}"
        " --no_offloads {}"
        " --duration {}"
        " --bottleneck_bw {}"
        " --results_dir {}".format(*combination, RESULTS_DIR)
    )
    print("CMD:\n", all_cmds[-1])

dir_name = time.strftime("ALL_COMBO_%d-%m_%H:%M:%S.dump")
os.mkdir(dir_name)
os.chdir(dir_name)

NUM_ITERATIONS = len(all_cmds) // NUM_PROCESSES
REM_CMDS_LEN = len(all_cmds) % NUM_PROCESSES

for i in tqdm(range(0, NUM_ITERATIONS)):
    procs = [
        Process(target=exec_subprocess, args=(cmd,))
        for cmd in all_cmds[i * NUM_PROCESSES : (i + 1) * NUM_PROCESSES]
    ]
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join()

for i in tqdm(range(REM_CMDS_LEN)):
    exec_subprocess(all_cmds[-(i + 1)])

os.chown(f"../{dir_name}", int(os.getenv("SUDO_UID")), int(os.getenv("SUDO_GID")))
