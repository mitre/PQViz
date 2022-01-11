import gzip
import json
from pathlib import Path
import shutil

import branca.colormap as cm
import geopandas as gpd
from ipyleaflet import (
    basemaps,
    Choropleth,
    GeoJSON,
    Icon,
    LayersControl,
    LegendControl,
    Map,
    Marker,
    Popup,
    WidgetControl,
)
from ipywidgets import Label, Layout, VBox
import ipywidgets as widgets
import numpy as np
import pandas as pd
import us


# ZCTA-ZIP Code mapping for filtering by state
Z2Z = pd.read_csv("reference_data/zcta-zip-mapping-2020.csv.gz")

# Note: DC is not included by default in the v2 release line; assure it's there
if us.states.DC not in us.STATES:
    us.STATES.append(us.states.DC)

# Convenience subset of "interesting" measures from CDC PLACES selected for
# variety and range of correlations at national level with Obesity
PLACES_MEASURES = [
    ("Total Population", "TotalPopulation", "ZCTA Population"),
    (
        "Access",
        "ACCESS2_CrudePrev",
        "Current lack of health insurance, crude prevalence among adults",
    ),
    ("Asthma", "CASTHMA_CrudePrev", "Current Asthma, crude prevalence among adults"),
    (
        "Cholesterol",
        "CHOLSCREEN_CrudePrev",
        "Cholesterol screening, crude prevalence among adults",
    ),
    (
        "Dental Visits",
        "DENTAL_CrudePrev",
        "Visits to dentist or dental clinic, crude prevalence among adults",
    ),
    (
        "Diabetes",
        "DIABETES_CrudePrev",
        "Diagnosed Diabetes, crude prevalence among adults",
    ),
    ("Obesity", "OBESITY_CrudePrev", "Obesity, crude prevalence among adults"),
]

# Color brewer colorblind safe diverging 6-class colors via
# https://colorbrewer2.org/?type=diverging&scheme=PRGn&n=6
COLOR_SCALE = ["#762a83", "#af8dc3", "#e7d4e8", "#d9f0d3", "#7fbf7b", "#1b7837"]

# Shorthand set of state-level bounding boxes for zooming to extent w/fit_bounds()
STATE_BOUNDS = json.load(open("reference_data/state_boundaries/state_bounds.json"))


def load_places(fname="reference_data/cdc-places-zcta-2020.csv"):
    """
    The CDC PLACES csv data is 20MB unzipped and gzips to 6MB, so it's included
    gzipped. Unzip if needed, because gpd doesn't seem to be able to handle gzipped
    data, even if gzip.open()'d inline.

    Parameters:
    fname: File path for CDC PLACES csv data

    Returns:
    A DataFrame containing CDC PLACES data.
    """
    if not Path(fname).is_file():
        with gzip.open(f"{fname}.gz", "rb") as f_in:
            with open(fname, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

    places = gpd.read_file(fname, dtype={"TotalPopulation": np.int32})
    return places


def choropleth_map_places(selected_state="AL", selected_measure="TotalPopulation"):
    # US state metadata
    us_state = us.states.lookup(selected_state)

    # Use ZCTA-ZIP Code mapping to filter by state
    state_zcta_list = Z2Z.loc[Z2Z["STATE"] == us_state.abbr]["ZCTA"].unique()

    # CDC PLACES data
    places = load_places()
    state_places = places.loc[places["ZCTA5"].isin(state_zcta_list)]

    # State-level boundary file in geojson
    state_gj_fname = Path(
        f"reference_data/state_boundaries/{selected_state}_zctas.geojson.gz"
    )
    state_gj = json.load(gzip.open(state_gj_fname, "r"))
    # Specify id key on all features (required for choropleth mapping to data)
    for feature in state_gj["features"]:
        properties = feature["properties"]
        feature.update(id=properties["ZCTA5CE10"])

    measure_display, measure_name, measure_desc = [
        mm for mm in PLACES_MEASURES if mm[0] == selected_measure
    ][0]
    if measure_name == "TotalPopulation":
        state_places[measure_name] = state_places[measure_name].astype(int)
    else:
        state_places[measure_name] = state_places[measure_name].astype(float)

    state_valmap = dict(
        zip(state_places["ZCTA5"].tolist(), state_places[measure_name].tolist())
    )
    if selected_measure == "Total Population":
        value_min = state_places[measure_name].min()
        value_max = state_places[measure_name].max()
    else:
        value_min = 0
        value_max = 100
    state_colors = cm.LinearColormap(
        COLOR_SCALE,
        vmin=value_min,
        vmax=value_max,
    ).to_step(10, method="quant")

    # TODO: Brute force assign meaningless value to ZCTAs not otherwise represented
    # in PLACES; evaluate for better options
    state_feature_ids = set([f["id"] for f in state_gj["features"]])
    state_valmap_ids = set(state_valmap.keys())
    for fid in state_feature_ids.difference(state_valmap_ids):
        state_valmap[fid] = 0

    m = Map()
    label = Label(layout=Layout(width="100%"))

    def click_handler(event=None, feature=None, id=None, properties=None):
        if selected_measure == "Total Population":
            value = f"{state_valmap[id]:,d}"
        else:
            value = f"{state_valmap[id]}%"
        label.value = f"ZCTA {properties['ZCTA5CE10']}: {value} ({measure_desc})"

    geo_data = Choropleth(
        geo_data=state_gj,
        choro_data=state_valmap,
        colormap=state_colors,
        value_min=value_min,
        value_max=value_max,
        border_color="black",
        hover_style={"fillOpacity": 0.4},
        style={"fillOpacity": 0.8},
        name=measure_display,
        layout=Layout(width="100%", height="600px"),
    )
    geo_data.on_click(click_handler)
    m.add_layer(geo_data)

    legend_colors = {}
    for val in state_colors.index:
        legend_key = (
            f"{round(val)}%"
            if selected_measure != "Total Population"
            else f"{int(val):,d}"
        )
        legend_colors[legend_key] = state_colors.rgb_hex_str(val)
    legend = LegendControl(legend_colors, name=measure_display, position="bottomright")
    m.add_control(legend)
    m.fit_bounds(STATE_BOUNDS[selected_state])

    return VBox([m, label])


def choropleth_map_pq(selected_state="NC", df=None, category="", prevalence_type=""):
    # US state metadata
    us_state = us.states.lookup(selected_state)

    # Filter to state-level ZCTAs
    state_zcta_list = Z2Z.loc[Z2Z["STATE"] == us_state.abbr]["ZCTA"].unique()

    # State-level boundary file in geojson
    state_gj_fname = Path(
        f"reference_data/state_boundaries/{selected_state}_zctas.geojson.gz"
    )
    state_gj = json.load(gzip.open(state_gj_fname, "r"))
    # Specify id key on all features (required for choropleth mapping to data)
    for feature in state_gj["features"]:
        properties = feature["properties"]
        feature.update(id=properties["ZCTA5CE10"])

    # Limit to selected category and type
    df = df.copy()
    # Eliminate suppressed values
    df = df.loc[df["Prevalence"].notna()]
    df = df.loc[df["Weight Category"] == category]
    df = df.loc[df["Prevalence type"] == prevalence_type]
    df["Prevalence"] = df["Prevalence"].astype(float)

    # Probably inefficient!
    valmap = {}
    for z5 in state_zcta_list:
        for z3 in df["zcta3"].tolist():
            if z5.startswith(z3):
                valmap[z5] = df.loc[df["zcta3"] == z3]["Prevalence"].values[0]

    value_min = 0
    value_max = 100
    value_set = np.array([x for x in valmap.values()])
    colors = cm.LinearColormap(
        COLOR_SCALE,
        vmin=value_min,
        vmax=value_max,
    ).to_step(10, method="quant")

    # Brute force removal of ZCTAs without a value in state-level geojson. not ideal.
    feature_ids = set([f["id"] for f in state_gj["features"]])
    valmap_ids = set(valmap.keys())
    for fid in feature_ids.difference(valmap_ids):
        valmap[fid] = 0
    reduced_features = [f for f in state_gj["features"] if valmap[f["id"]] != 0]
    state_gj["features"] = reduced_features

    m = Map()
    label = Label(layout=Layout(width="100%"))

    def click_handler(event=None, feature=None, id=None, properties=None):
        value = f"ZCTA3 {properties['ZCTA5CE10'][:3]}: {valmap[id]} ({prevalence_type} prevalence, {category})"
        label.value = value

    geo_data = Choropleth(
        geo_data=state_gj,
        choro_data=valmap,
        colormap=colors,
        value_min=value_min,
        value_max=value_max,
        border_color="black",
        hover_style={"fillOpacity": 0.4},
        style={"fillOpacity": 1.0},
        name=category,
        layout=Layout(width="100%", height="600px"),
    )
    geo_data.on_click(click_handler)
    m.add_layer(geo_data)

    legend_colors = {}
    for val in colors.index:
        legend_key = f"{round(val)}%"
        legend_colors[legend_key] = colors.rgb_hex_str(val)
    legend = LegendControl(legend_colors, name="PQ Prevalence", position="bottomright")
    m.add_control(legend)
    m.fit_bounds(STATE_BOUNDS[selected_state])

    return VBox([m, label])
