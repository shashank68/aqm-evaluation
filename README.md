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
- If an argument is not specified, the default value defined in [exp_config.py](./exp_config.py) is used
- The flent data file will be generated in a directory for each node.


Check additional notes/scripts [here](./misc_patch_scripts/)


To run tests with all combination of network configs, use:
```bash
python3 run_all_combinations.py
```
- You may need to change the python path in this script if you use a virtual environment or anaconda
