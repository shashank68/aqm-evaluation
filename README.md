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
sudo python3 dumbell_flent.py
```


- Use the following optional command line arguments 
```bash
sudo python3 dumbell_flent.py --rtt=100 --bottleneck_bw=80 --AQM=fq_codel --cong_control_algo=cubic --ecn=No --offloads=Yes
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
sudo patch /usr/share/flent/flent/runners.py < flent_runners_fq_pie.diff
```

- To use `qdisc_stats_interfaces` test parameter, Run the below command once:

```bash
sudo cp tc_iterate.sh /usr/share/flent/flent/scripts/
```

- The flent data file will be generated in a directory for each node.

To plot all graphs run:
```bash
python3 plot_all.py
```
- You may need to change the python path in this script if you use a virtual environment or anaconda


## Changing pie vars in kernel (For e.g: `burst_time` in `include/net/pie.h`)

- Get the kernel source
- Modify the code
- Run ```load_pies.sh``` in the kernel source root directory