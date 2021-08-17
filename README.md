# Flent tests on Dumbell Topology

## Requirements

* nitk-nest
* flent

## Usage

- All **Bold** variable names are configurable network parameters

```bash
sudo python3 dumbell_flent.py
```

### Note
To use `qdisc_stats_interfaces`, Run the below command once:
```bash
sudo cp tc_iterate.sh /usr/share/flent/flent/scripts/
```

- The flent data file will be generated in a directory for each node.