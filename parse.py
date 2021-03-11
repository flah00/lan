#!/usr/bin/env python
# vim:noexpandtab tabstop=4:
# ARGS
# 1: CSV file output is appended to
# 2: Name of the host, ie router, qn, etc
# 3: RFC 3339 date
# INPUT FORMAT
#     Busybox
#            RX packets:4806813 errors:0 dropped:0 overruns:0 frame:0
#            TX packets:14397505 errors:0 dropped:337318 overruns:0 carrier:0
#            RX bytes:548040115 (522.6 MiB)  TX bytes:564263154 (538.1 MiB)
#     PureOS
#            RX packets 106240110  bytes 47224470586 (43.9 GiB)
#            RX errors 0  dropped 0  overruns 0  frame 0
#            TX packets 101802126  bytes 50990335522 (47.4 GiB)
#            TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
import sys
import re
import os.path

if len(sys.argv) != 4:
	sys.exit(1)
output = sys.argv[1]
host_alias = sys.argv[2]
epoch = sys.argv[3]
# influx csv requirements
with open(output, "w") as f:
	f.write("#datatype measurement,tag,tag,tag,tag,field,dateTime:RFC3339\nm,iface,stat,dir,host,long,time\n")

for line in sys.stdin:
	m = re.match('^([\w.]+)', line)
	if m:
		if_name = m.group(1)
		continue

	busy_box_rx = re.search('RX packets:(\d*) errors:(\d*) dropped:(\d*) overruns:(\d*) frame:(\d*)', line)
	busy_box_tx = re.search('TX packets:(\d*) errors:(\d*) dropped:(\d*) overruns:(\d*) carrier:(\d*)', line)
	busy_box_pkt = re.search('RX bytes:(\d*) .*TX bytes:(\d*) ', line)

	pure_pkt_tx = re.search('TX packets (\d*) *bytes (\d*)', line)
	pure_pkt_rx = re.search('RX packets (\d*) *bytes (\d*)', line)

	pure_tx = re.search('TX errors (\d*) *dropped (\d*) *overruns (\d*) *carrier (\d*) *collisions (\d*)', line)
	pure_rx = re.search('RX errors (\d*) *dropped (\d*) *overruns (\d*) *frame (\d*)', line)

	if busy_box_pkt:
		with open(output, "a") as f:
			f.write("ifconfig,%s,bytes,rx,%s,%s,%s\n"  % (if_name, host_alias, busy_box_pkt.group(1), epoch))
			f.write("ifconfig,%s,bytes,tx,%s,%s,%s\n"  % (if_name, host_alias, busy_box_pkt.group(2), epoch))

	elif busy_box_tx:
		with open(output, "a") as f:
			f.write("ifconfig,%s,packets,tx,%s,%s,%s\n"  % (if_name, host_alias, busy_box_tx.group(1), epoch))
			f.write("ifconfig,%s,errors,tx,%s,%s,%s\n"   % (if_name, host_alias, busy_box_tx.group(2), epoch))
			f.write("ifconfig,%s,dropped,tx,%s,%s,%s\n"  % (if_name, host_alias, busy_box_tx.group(3), epoch))
			f.write("ifconfig,%s,overruns,tx,%s,%s,%s\n" % (if_name, host_alias, busy_box_tx.group(4), epoch))
			f.write("ifconfig,%s,carrier,tx,%s,%s,%s\n"  % (if_name, host_alias, busy_box_tx.group(5), epoch))

	elif busy_box_rx:
		with open(output, "a") as f:
			f.write("ifconfig,%s,packets,rx,%s,%s,%s\n"  % (if_name, host_alias, busy_box_rx.group(1), epoch))
			f.write("ifconfig,%s,errors,rx,%s,%s,%s\n"   % (if_name, host_alias, busy_box_rx.group(2), epoch))
			f.write("ifconfig,%s,dropped,rx,%s,%s,%s\n"  % (if_name, host_alias, busy_box_rx.group(3), epoch))
			f.write("ifconfig,%s,overruns,rx,%s,%s,%s\n" % (if_name, host_alias, busy_box_rx.group(4), epoch))
			f.write("ifconfig,%s,frame,rx,%s,%s,%s\n"    % (if_name, host_alias, busy_box_rx.group(5), epoch))

	elif pure_pkt_tx:
		with open(output, "a") as f:
			f.write("ifconfig,%s,packets,tx,%s,%s,%s\n" % (if_name, host_alias, pure_pkt_tx.group(1), epoch))
			f.write("ifconfig,%s,bytes,tx,%s,%s,%s\n"   % (if_name, host_alias, pure_pkt_tx.group(2), epoch))

	elif pure_pkt_rx:
		with open(output, "a") as f:
			f.write("ifconfig,%s,packets,rx,%s,%s,%s\n" % (if_name, host_alias, pure_pkt_rx.group(1), epoch))
			f.write("ifconfig,%s,bytes,rx,%s,%s,%s\n"   % (if_name, host_alias, pure_pkt_rx.group(2), epoch))

	elif pure_tx:
		with open(output, "a") as f:
			f.write("ifconfig,%s,errors,tx,%s,%s,%s\n"      % (if_name, host_alias, pure_tx.group(1), epoch))
			f.write("ifconfig,%s,dropped,tx,%s,%s,%s\n"     % (if_name, host_alias, pure_tx.group(2), epoch))
			f.write("ifconfig,%s,overruns,tx,%s,%s,%s\n"    % (if_name, host_alias, pure_tx.group(3), epoch))
			f.write("ifconfig,%s,carrier,tx,%s,%s,%s\n"     % (if_name, host_alias, pure_tx.group(4), epoch))
			f.write("ifconfig,%s,collisions,tx,%s,%s,%s\n"  % (if_name, host_alias, pure_tx.group(5), epoch))

	elif pure_rx:
		with open(output, "a") as f:
			f.write("ifconfig,%s,errors,rx,%s,%s,%s\n"      % (if_name, host_alias, pure_rx.group(1), epoch))
			f.write("ifconfig,%s,dropped,rx,%s,%s,%s\n"     % (if_name, host_alias, pure_rx.group(2), epoch))
			f.write("ifconfig,%s,overruns,rx,%s,%s,%s\n"    % (if_name, host_alias, pure_rx.group(3), epoch))
			f.write("ifconfig,%s,frame,rx,%s,%s,%s\n"       % (if_name, host_alias, pure_rx.group(4), epoch))

