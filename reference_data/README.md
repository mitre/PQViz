# Reference Data

This directory contains several files of reference data used in support of
PQViz. These data sources are in the public domain.

## CDC PLACES

The file `cdc-places-zcta-2020.csv.gz` is a compressed export of data from
[CDC PLACES](http://www.cdc.gov/places/). It was obtained in CSV format via this
link in January 2022:

    https://chronicdata.cdc.gov/500-Cities-Places/PLACES-ZCTA-Data-GIS-Friendly-Format-2021-release/kee5-23sr

It is stored compressed to save space and bandwidth, but will be uncompressed
when it is used in PQViz due to a minor quirk in the code used to read it.

## ZIP Code to ZCTA mapping

The file `cdc-places-zcta-2020.csv` is a CSV export of data from the
[ZIP Code to ZCTA Crosswalk](https://udsmapper.org/zip-code-to-zcta-crosswalk/)
available from the [UDS Mapper](https://udsmapper.org/). It was obtained in
Excel format in January 2022 and converted to CSV manually.

## State boundary files

The directory `state-boundaries` includes one geojson file containing the ZCTA
boundaries for the 50 US states plus DC. These are derived from the US Census
[Cartographic Boundary Files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2019.html),
and the
[UDS Mapper ZCTA to ZIP Code Crosswalk](https://udsmapper.org/zip-code-to-zcta-crosswalk/)
data. A Python script in this directory, `create-state-boundaries.py`, uses
these files to generate the individual state files and a set of extents for each
state for use within the notebook. The script has been used to create the files
present in this directory, which were also compressed to save space, and the use
of the script is not required to use the notebook itself. It is included to
support potential maintenance. See the script for additional details on its use.
