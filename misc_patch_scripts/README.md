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

- To use `qdisc_stats_interfaces` test parameter and to speed up flent execution, Use the provided iterators:

```bash
sudo cp tc_iterate.sh ss_iterate.sh /usr/share/flent/flent/scripts/
```

- Apply the given patch to support link utilization plots

```bash
sudo patch /usr/share/flent/flent/tests/tcp_nup.conf tcp_nup.conf.diff
sudo patch /usr/share/flent/flent/tests/tcp_stats.inc tcp_stats.inc.diff
```