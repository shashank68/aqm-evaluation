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

usage: dumbell_flent.py [-h] [--rtt RTT] [--ecn {Yes,No}] [--duration TIME] [--bottleneck_bw BANDWIDTH] [--qdisc {fq_codel,fq_pie,codel,pie,cake}] [--no_offloads {Yes,No}] [--number_of_tcp_flows NUM] [--qdelay_target TARGET]

optional arguments:
  -h, --help            show this help message and exit
  --rtt RTT             Round trip time for flows (ms)
  --ecn {Yes,No}        Turn on ECN
  --duration TIME       Duration of test in seconds
  --bottleneck_bw BANDWIDTH
                        Bottleneck bandwidth (mbit)
  --qdisc {fq_codel,fq_pie,codel,pie,cake}
                        AQM algorithm (qdisc)
  --no_offloads {Yes,No}
                        Turn off GSO, GRO offloads
  --number_of_tcp_flows NUM
                        Number of flows in tcp_nup flent test
  --qdelay_target TARGET
                        Queue delay target (For qdisc)
```


- Example Usage 
```bash
sudo python3 dumbell_flent.py --rtt=100 --bottleneck_bw=80 --qdisc=fq_codel --ecn=No --no_offloads=Yes
```
- If an argument is not specified, the default value defined in [exp_config.py](./exp_config.py) is used
- The flent data file will be generated in a directory for each node.


Check additional notes/scripts [here](./misc_patch_scripts/)


* To run tests with all combination of network configs run, 
```bash
cp combinations_config.json.example combinations_config.json
```
and set the parameters required in `combinations_config.json` and run:
```bash
python3 run_all_combinations.py
```
- You may need to change the python path in this script if you use a virtual environment or anaconda
