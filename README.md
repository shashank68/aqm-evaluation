#  AQM (qdisc) Evaluation using flent tests

## Requirements Setup

`FQ_PIE` AQM support in **iproute2** was added from _version 5.5_.
* To install iproute2 with fq_pie support (e.g: v5.7)

```bash
wget http://in.archive.ubuntu.com/ubuntu/pool/main/i/iproute2/iproute2_5.7.0-1ubuntu1_amd64.deb
sudo apt install ./iproute2_5.7.0-1ubuntu1_amd64.deb
```

* nitk-nest

```bash
python3 -m pip install nitk-nest
```

* flent

```bash
sudo add-apt-repository ppa:tohojo/flent
sudo apt install flent
```

* Apply the given patch to parse fq_pie qdisc stats in flent
```bash
sudo patch /usr/share/flent/flent/runners.py < misc_patch_scripts/flent_runners_fq_pie.diff
```

* To use `qdisc_stats_interfaces` test parameter and to speed up flent execution, Use the provided iterators:

```bash
sudo cp misc_patch_scripts/tc_iterate.sh misc_patch_scripts/ss_iterate.sh /usr/share/flent/flent/scripts/
```

* Apply the given patch to support link utilization plots

```bash
sudo patch /usr/share/flent/flent/tests/tcp_nup.conf misc_patch_scripts/tcp_nup.conf.diff
sudo patch /usr/share/flent/flent/tests/tcp_stats.inc misc_patch_scripts/tcp_stats.inc.diff
```

* Clone/Download the repository

```bash
git clone https://github.com/shashank68/flent-aqm-tests
```


## Usage

Use the `--help` option to view configurable network parameters

```bash
sudo python dumbbell_flent.py --help

usage: dumbbell_flent.py [-h] [--rtt RTT] [--ecn {Yes,No}] [--duration TIME] [--bottleneck_bw BANDWIDTH] [--qdisc {fq_codel,fq_pie,codel,pie,cake}] [--no_offloads {Yes,No}] [--number_of_tcp_flows NUM] [--qdelay_target TARGET]

optional arguments:
  -h, --help            show this help message and exit
  --rtt RTT             Round trip time for flows (ms)
  --ecn {Yes, No}        Turn on ECN
  --duration TIME       Duration of test in seconds
  --bottleneck_bw BANDWIDTH
                        Bottleneck bandwidth (mbit)
  --qdisc {fq_codel, fq_pie, codel, pie, cake}
                        AQM algorithm (qdisc)
  --no_offloads {Yes, No}
                        Turn off GSO, GRO offloads
  --number_of_tcp_flows NUM
                        Number of flows in tcp_nup flent test
  --qdelay_target TARGET
                        Queue delay target (For qdisc)
```
If any of the above arguments are not specified, their default values defined in [exp_config.py](./exp_config.py) are used

Example Usage 
```bash
sudo python3 dumbbell_flent.py --rtt=100 --bottleneck_bw=80 --qdisc=fq_codel --ecn=No --no_offloads=Yes
```
* The flent data file will be generated in a directory for each node.
* The above script will create a directory `fq_codel_1_80_100_27-09_18:43:53.dump`


Check additional notes/scripts [here](./misc_patch_scripts/)


## Running Multiple tests

* To run tests with custom combination of parameters, create a `combinations_config.json`
```bash
cp combinations_config.json.example combinations_config.json
```
* Modify the values in `combinations_config.json` if required
* To execute tests with the configured parameters run:
```bash
sudo python run_all_combinations.py
```
* If you do not create a `combinations_config.json` file then the default values in `run_all_combinations.py` will be used

