#!/bin/bash
for f in osm_pbf_countries_big/* ; do
#name="$(basename $f)"
name=${f##*/}
echo working on "$name"
osmium tags-filter -o "osm_pbf/$name" "$f" w/highway,usage=motorway,trunk,main
done
