# Import modules
import os
import pandas as pd
import plotly.express as px
import json

import gunicorn  # (version 20.1.0)

import dash  # (version 1.8.0)
from dash import dcc
from dash import html
from dash import callback_context
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# Set paths and directories
IN_PATH = os.path.join("data/clean", "COUNTY_AGGREGATE_FIPS.csv")
IN_PATH_JSON = os.path.join("data/raw", "geojson-counties-fips.json")
IN_PATH_2 = os.path.join("data/clean", "ST_Agg_Fips_Merge.csv")
IN_PATH_JSON_2 = os.path.join("data/raw", "us-states.json")
IN_PATH_3 = os.path.join("data/clean", "ST_yoy_avg_fips_Merge.csv")
IN_PATH_4 = os.path.join("data/clean", "CTY_Fips_Merge.csv")

# takes the appropriate dataframes and saves them into objects for building choropleths:

# State level data:
state_fips = pd.read_csv(IN_PATH_2, dtype={"FIPS": str})
with open(IN_PATH_JSON_2) as response:
    states = json.load(response)

state_fips_yoy = pd.read_csv(IN_PATH_3, dtype={"FIPS": str})

# County level data:
county_fips = pd.read_csv(IN_PATH, dtype={"FIPS": str})
with open(IN_PATH_JSON) as response:
    counties = json.load(response)

county_fips_yoy = pd.read_csv(IN_PATH_4, dtype={"FIPS": str})

# Creating object with Acceptable State Names:
state_names = county_fips["STNAME"].unique()

# Making app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# setting server
server = app.server

# applying layout
app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Dropdown(
                    options=["Percent Change", "Median Price"],
                    value="Percent Change",
                    id="dropdown",
                    clearable=False,
                    className="string",
                )
            ]
        ),
        html.Div([dcc.Graph(id="the_graph")]),
        html.Div(
            [
                dcc.Input(
                    id="input_state",
                    type="text",
                    value="USA",
                    required=True,
                    autoComplete="on",
                ),
                html.Button(id="go_button", n_clicks=0, children="GO!"),
                html.Div(id="output_state"),
            ],
            style={"text-align": "center"},
        ),
    ]
)


@ app.callback(
    [
        Output("output_state", "children"),
        Output(component_id="the_graph", component_property="figure"),
    ],
    [
        Input(component_id="go_button", component_property="n_clicks"),
    ],
    [
        State(component_id="dropdown", component_property="value"),
        State(component_id="input_state", component_property="value"),
    ],
)
def update_output(num_clicks, drops, val_selected):
    if drops == "Percent Change":
        # State level % change map
        if val_selected == "USA":
            fig = px.choropleth(
                state_fips,
                geojson=states,
                locations="FIPS",
                color="Change_From_2010",
                hover_name="STNAME",
                hover_data={"FIPS": False},
                color_continuous_scale="PuBu",
                range_color=(0, 100),
                scope="usa",
                labels={"Change_From_2010": "Percent Change "},
                title="Percent Change in House Values from 2010-2019 by State",
            )
            fig.update_layout(
                hoverlabel=dict(bgcolor="black", font_size=16,
                                font_family="Rockwell"),
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
            )
            return (
                "Type in a state name above to retrieve county level data!",
                fig,
            )
        # County level % change map
        if val_selected in state_names:  # County wide choropleth
            df = county_fips[county_fips["STNAME"] == val_selected]

            fig = px.choropleth(
                df,
                geojson=counties,
                locations="FIPS",
                color="New_percent_change",
                hover_name="CTYNAME",
                hover_data={"FIPS": False},
                color_continuous_scale="PuBu",
                range_color=(0, 100),
                scope="usa",
                labels={"New_percent_change": "Percent Change "},
                title="Percent Change in House Values from 2010-2019 by County",
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(
                hoverlabel=dict(bgcolor="black", font_size=16,
                                font_family="Rockwell"),
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
            )
            return (
                "Want to see pricing information? Try the dropdown menu at the top then hit GO!.",
                fig,
            )
        # reverts back to state level map if there is an invalid input
        else:
            fig = px.choropleth(
                state_fips,
                geojson=states,
                locations="FIPS",
                color="Change_From_2010",
                hover_name="STNAME",
                hover_data={"FIPS": False},
                color_continuous_scale="PuBu",
                range_color=(0, 100),
                scope="usa",
                labels={"Change_From_2010": "Percent Change "},
                title="Percent Change in House Values from 2010-2019 by State",
            )
            fig.update_layout(
                hoverlabel=dict(bgcolor="black", font_size=16,
                                font_family="Rockwell"),
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
            )
            return (
                "Please enter a valid state name (first letter must be capitalized)",
                fig,
            )

    if drops == "Median Price":
        # State level pricing map
        if val_selected == "USA":
            fig = px.choropleth(
                state_fips_yoy,
                geojson=states,
                locations="FIPS",
                color="W_PRICE",
                hover_name="STNAME",
                hover_data={"FIPS": False, "YEAR": False},
                color_continuous_scale="PuBu",
                range_color=(0, 600000),
                scope="usa",
                labels={"W_PRICE": "Weighted Price"},
                animation_frame="YEAR",
                title="Year-Over-Year Change in Weighted Mean Price per State",
            )
            fig.update_layout(
                hoverlabel=dict(bgcolor="black", font_size=16,
                                font_family="Rockwell"),
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
            )
            return (
                "Type in a state name above to retrieve county level data!",
                fig,
            )
        # County level pricing map
        if val_selected in state_names:
            df = county_fips_yoy[county_fips_yoy["STNAME"] == val_selected]
            fig = px.choropleth(
                df,
                geojson=counties,
                locations="FIPS",
                color="PRICE",
                hover_name="CTYNAME",
                hover_data={"FIPS": False, "YEAR": False},
                color_continuous_scale="PuBu",
                scope="usa",
                labels={"PRICE": "Housing Price"},
                animation_frame="YEAR",
                title="Change in House Values Over Time by County",
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(
                hoverlabel=dict(bgcolor="black", font_size=16,
                                font_family="Rockwell"),
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
            )
            return (
                "Cool right!? Try another one :)",
                fig,
            )
        # reverts back to state level map with invalid input
        else:
            fig = px.choropleth(
                state_fips_yoy,
                geojson=states,
                locations="FIPS",
                color="W_PRICE",
                hover_name="STNAME",
                hover_data={"FIPS": False, "YEAR": False},
                color_continuous_scale="PuBu",
                range_color=(0, 600000),
                scope="usa",
                labels={"W_PRICE": "Weighted Price"},
                animation_frame="YEAR",
                title="Year-Over-Year Change in Weighted Mean Price per State",
            )
            fig.update_layout(
                hoverlabel=dict(bgcolor="black", font_size=16,
                                font_family="Rockwell"),
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
            )
            return (
                "Please enter a valid state name (first letter must be capitalized)",
                fig,
            )


# loading screen?
app.css.append_css(
    {"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
