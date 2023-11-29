import argparse
import multiprocessing
import os
import pathlib

import geojson
import osmium as o


class ExtractNetworkHandler(o.SimpleHandler):
    def __init__(self):
        super(ExtractNetworkHandler, self).__init__()
        self.roads = []
        self.rails = []
        self.highway_types = {"motorway", "trunk"}
        self.loaded = False

    def way(self, w):
        if not self.loaded:
            self.loaded = True
            print("Loaded file. Starting filtering")
        if w.tags.get("railway") == "rail" and w.tags.get("usage") == "main":
            if len(self.rails) % 1000 == 0:
                print(f"Found {len(self.rails)} rails...")
            self.rails.append(geojson.LineString([(n.lon, n.lat) for n in w.nodes]))

        if w.tags.get("highway") in self.highway_types:
            if len(self.roads) % 1000 == 0:
                print(f"Found {len(self.roads)} roads...")
            self.roads.append(geojson.LineString([(n.lon, n.lat) for n in w.nodes]))


def get_networks(full_fname):
    assert full_fname.endswith(".osm.pbf")
    print(f"Processing {full_fname}")

    handler = ExtractNetworkHandler()
    handler.apply_file(full_fname, locations=True)
    print(f"Found {len(handler.roads)} roads and {len(handler.rails)} rails")

    return handler.roads, handler.rails


def extract_file(in_file, out_file_roads, out_file_rails):
    roads, rails = get_networks(in_file)

    with open(out_file_roads, "w") as f:
        geojson.dump(geojson.GeometryCollection(roads), f)
    with open(out_file_rails, "w") as f:
        geojson.dump(geojson.GeometryCollection(rails), f)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir",
        default=f"{script_dir}/osm_pbf",
        help="the directory with the osm.pbf files",
    )
    parser.add_argument(
        "--output-rails",
        default=f"{script_dir}/rails_geojson",
        help="the to place the geojson rail files",
    )
    parser.add_argument(
        "--output-roads",
        default=f"{script_dir}/roads_geojson",
        help="the to place the geojson road files",
    )
    parser.add_argument(
        "--no-combine",
        default=False,
        help="Don't create the combined file",
        action="store_true",
    )
    parser.add_argument(
        "--clean",
        default=False,
        help="Remove any previous geojson files before running",
        action="store_true",
    )
    opt = parser.parse_args()

    rail_dir = pathlib.Path(opt.output_rails)
    road_dir = pathlib.Path(opt.output_roads)
    if opt.clean:
        for child in list(road_dir.glob("*")) + list(rail_dir.glob("*")):
            child.unlink()

    rail_dir.mkdir(parents=True, exist_ok=True)
    road_dir.mkdir(parents=True, exist_ok=True)

    args = [
        (
            f"{opt.input_dir}/{fname}",
            f"{opt.output_roads}/{fname[: -len('.osm.pbf')]}_roads.geojson",
            f"{opt.output_rails}/{fname[: -len('.osm.pbf')]}_rails.geojson",
        )
        for fname in os.listdir(opt.input_dir)
    ]
    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        p.starmap(extract_file, args)

    if not opt.no_combine:
        rail_features = []
        for fname in os.listdir(opt.output_rails):
            if fname == "combined_rails.geojson":
                continue
            full_fname = f"{opt.output_rails}/{fname}"
            with open(full_fname) as f:
                rail_features.extend(geojson.load(f)["geometries"])
        with open(f"{opt.output_rails}/combined_rails.geojson", "w") as f:
            geojson.dump(geojson.GeometryCollection(rail_features), f)

        road_features = []
        for fname in os.listdir(opt.output_roads):
            if fname == "combined_roads.geojson":
                continue
            full_fname = f"{opt.output_roads}/{fname}"
            with open(full_fname) as f:
                road_features.extend(geojson.load(f)["geometries"])
        with open(f"{opt.output_roads}/combined_roads.geojson", "w") as f:
            geojson.dump(geojson.GeometryCollection(road_features), f)
