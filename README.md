# osm-planet-rail-road-scraper

Extracts the railroad and road networks from the osm planet files

## Requirements

All I know is that it works in 3.11.3 with osmium 3.7 and geojson 3.1 on
archlinux, but it probably works with anything. Let me know in the comments
below ;)

## Setup

```
pip install -r requirements.txt
```

## Usage

- Download the `*.osm.pbf` files that you want the rail and road networks of to
  a new `osm_pbf` directory inside the repo
- Run

```
python extract_networks.py
```

- Wait
- In `rails_geojson`, you will see a `combined_rails.geojson` and in
  `roads_geojson`, you will see a `combined_roads.geojson`. These are the final
  output files. There are also the intermediate files in that directory, one
  for each input file.

## Other Options

> Yep, this is just the -h pasted here

```
usage: extract_networks.py [-h] [--input-dir INPUT_DIR] [--output-rails OUTPUT_RAILS]
                           [--output-roads OUTPUT_ROADS] [--no-combine] [--clean]

options:
  -h, --help            show this help message and exit
  --input-dir INPUT_DIR
                        the directory with the osm.pbf files
  --output-rails OUTPUT_RAILS
                        the to place the geojson rail files
  --output-roads OUTPUT_ROADS
                        the to place the geojson road files
  --no-combine          Don't create the combined file
  --clean               Remove any previous geojson files before running
```
