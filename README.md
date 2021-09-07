# Flent tests on Dumbell Topology

## Requirements Setup

* nitk-nest

```bash
python3 -m pip install nitk-nest
```

* flent

```bash
sudo add-apt-repository ppa:tohojo/flent
sudo apt install flent
```

* Clone/Download the repository

```bash
git clone https://github.com/shashank68/flent-aqm-tests
```


## Usage

- All **Bold** variable names are configurable network parameters

```bash
sudo python dumbell_flent.py --help
usage: dumbell_flent.py [-h] [--rtt RTT] [--bottleneck_bw BOTTLENECK_BW] [--qdisc QDISC] [--ecn ECN] [--no_offloads NO_OFFLOADS] [--number_of_tcp_flows NUMBER_OF_TCP_FLOWS] [--qdelay_target QDELAY_TARGET]

optional arguments:
  -h, --help            show this help message and exit
  --rtt RTT             RTT of flows(ms)
  --bottleneck_bw BANDWIDTH
                        bottleneck bandwidth (mbit)
  --qdisc QDISC         AQM (qdisc) algorithm
  --ecn ECN             ecn flag (Yes / No)
  --no_offloads NO_OFFLOADS
                        Turn off GSO, GRO offloads (Yes / No)
  --number_of_tcp_flows NUMBER_OF_TCP_FLOWS
                        Number of flows (tcp_nup flent test)
  --qdelay_target QDELAY_TARGET
                        Queue delay target (For AQM)
```


- Example Usage 
```bash
sudo python3 dumbell_flent.py --rtt=100 --bottleneck_bw=80 --qdisc=fq_codel --ecn=No --no_offloads=Yes
```
- If an argument is not specified the value in the script is used

## Notes
- `FQ_PIE` AQM support in **iproute2** was added from _version 5.5_.
- To install iproute2 with fq_pie support (e.g: v5.7)

```bash
wget http://in.archive.ubuntu.com/ubuntu/pool/main/i/iproute2/iproute2_5.7.0-1ubuntu1_amd64.deb
sudo apt install ./iproute2_5.7.0-1ubuntu1_amd64.deb
```

- Apply the given patch to parse fq_pie qdisc stats in flent
```bash
sudo patch /usr/share/flent/flent/runners.py < misc_patch_scripts/flent_runners_fq_pie.diff
```

- To use `qdisc_stats_interfaces` test parameter, Run the below command once:

```bash
sudo cp misc_patch_scripts/tc_iterate.sh /usr/share/flent/flent/scripts/
```

- The flent data file will be generated in a directory for each node.

To plot all graphs run:
```bash
python3 plot_all.py
```
- You may need to change the python path in this script if you use a virtual environment or anaconda
