set -x

make -j8 M=net/sched
rmmod sch_fq_pie
rmmod sch_pie
insmod net/sched/sch_pie.ko
insmod net/sched/sch_fq_pie.ko
