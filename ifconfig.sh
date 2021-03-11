#!/bin/bash
# Write ifconfig rx and tx stats to influx
# ENV
# DEBUG: do not delete mktemp dir
# INFLUX_ORG: optional env var, -o overrides
# INFLUX_BUCKET: optional env var, -b overrides
# CRONTAB
# * * * * * /share/homes/admin/ifconfig/ifconfig.sh root@192.168.1.1 router TOKEN
# * * * * * /share/homes/admin/ifconfig/ifconfig.sh localhost qn TOKEN
export PATH=$PATH:/share/CE_CACHEDEV1_DATA/.qpkg/container-station/bin

function usage() {
  cat <<EOT
${0##*/} {-h SSH_USER_HOST} {-a HOST_ALIAS} {-t INFLUX_TOKEN} [...]
  -h STR  USER@IP or localhost
  -a STR  host nickname, influxdb tag
  -t STR  influxdb token
  -d PATH path to ifconfig output, skips ssh
  -o STR  influxdb org (default $INFLUX_ORG)
  -b STR  influxdb bucket (default $INFLUX_BUCKET)

EOT
}
INFLUX_ORG=${INFLUX_ORG:-lan}
INFLUX_BUCKET=${INFLUX_BUCKET:-home}
EXIT=0
while getopts h:a:t:d:o:b arg; do
  case $arg in
    # required
    a) ALIAS=$OPTARG;;
    h) HOST=$OPTARG;;
    t) TOKEN=$OPTARG;;
    # optional
    b) INFLUX_BUCKET=$OPTARG;;
    d) DEBUG_INPUT=$OPTARG; DEBUG=true; set -x;;
    o) INFLUX_ORG=$OPTARG;;
    *) usage; exit;;
  esac
done
if [[ $DEBUG = true ]]; then
  echo LOG /tmp/ifconfig.$$.log 
  exec >/tmp/ifconfig.$$.log 2>&1
fi
echo ${HOST:?Missing host} >/dev/null
echo ${ALIAS:?Missing alias name} >/dev/null
echo ${TOKEN:?Missing token} >/dev/null
# busybox date is a little funny
TIME=$(date --rfc-3339=seconds| sed 's/ /T/')
DIR=$(mktemp -u)
OUTPUT=$DIR/out.csv
mkdir -p $DIR
trap '[ "$DEBUG" != true ] && rm -rf $DIR; [[ $EXIT != 0 ]] && exit $EXIT' EXIT
trap '[ "$DEBUG" != true ] && rm -rf $DIR; exit 1' TERM INT

if [[ -f $DEBUG_INPUT ]]; then
  cp $DEBUG_INPUT $DIR/ifconfig
elif [[ $HOST =~ localhost ]]; then
  ifconfig > $DIR/ifconfig
else
  ssh -o ConnectTimeout=3 $HOST ifconfig > $DIR/ifconfig
  [[ $? -ne 0 ]] && exit 2
fi

SCRIPT=${0%/*}/parse.py
$SCRIPT $OUTPUT $ALIAS "$TIME" < $DIR/ifconfig 

docker cp $DIR influxdb:/tmp
docker exec -t influxdb influx write -o lan -b home -t $TOKEN --errors-file $DIR/influx-errors -f $OUTPUT
docker exec -t influxdb rm -rf $DIR

if [[ -e $DIR/influx-errors ]] && [[ ! -s $DIR/influx-errors ]]; then
  cat $DIR/influx-errors 1>&2
  EXIT=$(wc -l $DIR/influx-errors)
fi

if [[ $DEBUG = true ]]; then
  echo =======
  cat $OUTPUT
fi
