# LAN scripts

Store ifconfig stats, including RX/TX errors, drops, overruns, packets, in an influxdb
Stats are stored in a bucket, the measurement is called ifconfig
Tags are
    * iface
    * stat
    * dir
    * host

* ifconfig.sh: collect ifconfig output, insert into local docker influxdb
    * ENVVAR DEBUG: Do not delete mktemp dir if set to `true`, write stdout and stderr to `/tmp/ifconfig.$$.log`
    * Exits non-zero, if influx generates an error file
* parse.py: extract ifconfig stats, convert to csv
    * ARG 1: csv output file
    * ARG 2: host alias, is an influxdb tag
    * ARG 3: RFC 3339 date
