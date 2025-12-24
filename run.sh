#! /bin/bash
set -e

host="${id:-127.0.0.1}"

while [ $# -gt 0 ]; do
    if [[ $1 == "--"* ]]; then
        v="${1/--/}"
        declare "$v"="$2"
        shift
    fi
    shift
done

DIR="$(cd "$(dirname "$0")" && pwd)"

(cd $DIR/datacollection && python3 -m poetry run python3 datacollection --host "$host" --port 8080 --output $DIR/coordinates.csv)
(cd $DIR/plotting && python3 -m poetry run python3 plotting --data $DIR/coordinates.csv)