import os
import glob
from nest.engine import exec_subprocess

# get the flent result file name
all_flent_result_files = glob.glob("../*/*/*/*/*/*/*/*/*.gz")

BASE_DIR = os.getcwd()

# for each plot, extract the image
plot_titles = [
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

for result_file in all_flent_result_files:
    res_file = os.path.basename(result_file)
    res_dir = os.path.dirname(result_file)
    os.chdir(f"{BASE_DIR}/{res_dir}")
    os.makedirs("plots", exist_ok=True)
    for plot_title in plot_titles:
        exec_subprocess(
            f"flent {res_file} --plot {plot_title} -o plots/{plot_title}.png"
        )
