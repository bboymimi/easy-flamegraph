#
# Regular cron jobs for the easy-flamegraph package
#
0 4	* * *	root	[ -x /usr/bin/easy-flamegraph_maintenance ] && /usr/bin/easy-flamegraph_maintenance
