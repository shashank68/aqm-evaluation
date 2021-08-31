#Simple script to run dumbell_flent.py script

import subprocess

for TOTAL_LATENCY in [4, 40, 80, 800]:
    for BOTTLENECK_BANDWIDTH in [80, 160, 1000]:
        for AQM in ["fq_codel", "fq_pie"]:
            for TCP_CONG_CONTROL in ["cubic", "reno"]:
                for ECN in ["No", "Yes"]:
                    for OFFLOADS in ["No", "Yes"]:
                        for TOTAL_NODES_PER_SIDE in [1, 3, 16]:
                            for TARGET in [5]:
                                print(".")
                                process = subprocess.run([
                                    f"sudo",
                                    f"-S",
                                    f"/home/aditya/Documents/VII_Sem/MajorProject/majproj_tests/bin/python", # Change the python path here if you use a virtual environment
                                    f"dumbell_flent.py",
                                    f"--rtt={TOTAL_LATENCY}",
                                    f"--bottleneck_bw={BOTTLENECK_BANDWIDTH}",
                                    f"--AQM={AQM}",
                                    f"--cong_control_algo={TCP_CONG_CONTROL}",
                                    f"--ecn={ECN}",
                                    f"--offloads={OFFLOADS}",
                                    f"--number_of_flows={TOTAL_NODES_PER_SIDE}",
                                    f"--target={TARGET}"
                                    ],
                                    stdout=subprocess.PIPE,
                                    capture_output=False
                                )
                                print(process)

