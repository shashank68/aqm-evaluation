#Simple script to run dumbell_flent.py script

import subprocess

for TOTAL_LATENCY in [4, 40, 80, 800]:
    for BOTTLENECK_BANDWIDTH in [80, 160, 1000]:
        for AQM in ["fq_codel", "fq_pie", "cake"]:
            for ECN in ["No", "Yes"]:
                for OFFLOADS in ["No", "Yes"]:
                    for UPLOAD_STREAMS in [1, 3, 16]:
                        print(".")
                        process = subprocess.run([
                            f"python", # Change the python path here if you use a virtual environment
                            f"dumbell_flent.py",
                            f"--rtt={TOTAL_LATENCY}",
                            f"--bottleneck_bw={BOTTLENECK_BANDWIDTH}",
                            f"--qdisc={AQM}",
                            f"--ecn={ECN}",
                            f"--no_offloads={OFFLOADS}",
                            f"--number_of_tcp_flows={UPLOAD_STREAMS}",
                            ],
                            stdout=subprocess.PIPE,
                            capture_output=False
                        )
                        print(process)

