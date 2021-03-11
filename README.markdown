# LAN scripts

Store ifconfig stats, including RX/TX errors, drops, overruns, packets, in an influxdb

Stats are stored in a bucket, the measurement is called ifconfig

## Influx tags

* __iface__: eth0, lo, etc
* __stat__: errors, dropped, overruns, etc
* __dir__: tx or tx
* __host__: the alias tag assigned by `ifconfig.sh`

## Scripts

* `ifconfig.sh`: collect ifconfig output, insert into local docker influxdb
    * __ENVVAR DEBUG__: Do not delete mktemp dir if set to `true`, write stdout and stderr to `/tmp/ifconfig.$$.log`
    * Exits non-zero, if influx generates an error file
* `parse.py`: extract ifconfig stats, convert to csv
    * __ARG 1__: csv output file
    * __ARG 2__: host alias, an influxdb tag
    * __ARG 3__: RFC 3339 date

## Influx Query

```
from(bucket: "home")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "ifconfig")
  |> filter(fn: (r) => r["_field"] == "long")
  |> filter(fn: (r) => r["dir"] == "rx" or r["dir"] == "tx")
  |> filter(fn: (r) => r["host"] == "router")
  |> filter(fn: (r) => r["iface"] == "eth1")
  |> filter(fn: (r) => r["stat"] == "dropped" or r["stat"] == "errors" or r["stat"] == "overruns")
  |> aggregateWindow(every: 1m, fn: last, createEmpty: false)
  |> yield(name: "last")
```
