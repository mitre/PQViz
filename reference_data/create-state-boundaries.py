#!/usr/bin/env python

"""
create-state-boundaries.py

Create individual ZIP Code Tabulation Area (ZCTA) boundary files for each of the
50 US states plus DC in geojson, along with one additional file containing the
extent of each state boundary set.

This requires a local copy of the ZCTA shapefile available from the US Census,
at
https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2019.html.
Download the ZCTA shapefile and unzip it before running this script.

To obtain the extent of each file, this script opens a process to run
geojson-extent (https://github.com/mapbox/geojson-extent), which must be
installed and present on the system. These extent values support automatic
zooming to each state in the notebook.
"""

import argparse
import gzip
import json
import os
from pathlib import Path
import subprocess

import geopandas as gpd
import pandas as pd
import us


# DC is not included by default in the v2 release line; assure it's there
if us.states.DC not in us.STATES:
    us.STATES.append(us.states.DC)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "ZCTASHAPEFILE", default="cb_2019_us_zcta510_500k.shp", help="ZCTA shapefile"
    )
    parser.add_argument(
        "--dirname",
        default="state_boundaries",
        help="Directory to write boundary file into",
    )
    parser.add_argument(
        "--zctamappingfile",
        default="zcta-zip-mapping-2020.csv.gz",
        help="ZCTA to ZIP CODE mapping file",
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help="Show verbose output"
    )
    return parser.parse_args()


def main(args):
    if args.debug:
        print(f"Loading ZCTA shapefile {args.ZCTASHAPEFILE}")
    zctas = gpd.read_file(Path(args.ZCTASHAPEFILE))
    if args.debug:
        print(f"Loading ZCTA-ZIP mapping file {args.zctamappingfile}")
    z2z = pd.read_csv(Path(args.zctamappingfile))

    outdir = Path(args.dirname)
    os.makedirs(outdir, exist_ok=True)

    state_bounds = {}
    topo_state_bounds = {}
    for s in us.STATES:
        abbr = s.abbr
        if args.debug:
            print(f"Preparing ZCTA boundary file for {abbr}")
        fname = outdir / f"{abbr}_zctas.geojson"
        s_zctas_ids = z2z.loc[z2z["STATE"] == abbr]["ZCTA"].unique()
        s_zctas = zctas.loc[zctas["ZCTA5CE10"].isin(s_zctas_ids)]
        s_zctas.to_file(fname, driver="GeoJSON")

        if args.debug:
            print(f"...and computing extent")
        # specify `leaflet` to get in [[s, w], [n, e]] format
        extent_cmd = f"geojson-extent leaflet < {fname}"
        extent_result = subprocess.check_output(extent_cmd, shell=True)
        state_bounds[abbr] = json.loads(extent_result)

    bounds_fname = outdir / "state_bounds.json"
    if args.debug:
        print(f"Writing state bounds file to {bounds_fname}")
    json.dump(state_bounds, open(bounds_fname, "w"))


if __name__ == "__main__":
    args = parse_args()
    main(args)
