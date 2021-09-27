#  AQM (qdisc) Evaluation using flent tests

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

* Install the updated version of iproute2, copy the interators, and apply the required patches mentioned [here](./misc_patch_scripts/README.md)

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

