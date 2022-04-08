###### Import modules
import os
import pandas as pd
import plotly.express as px
import json


import dash  # (version 1.8.0)
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

###### Set paths and directories
IN_PATH = os.path.join("data/clean", "COUNTY_AGGREGATE_FIPS.csv")
IN_PATH_JSON = os.path.join("data/raw", "geojson-counties-fips.json")
IN_PATH_2 = os.path.join("data/clean", "ST_Agg_Fips_Merge.csv")
IN_PATH_JSON_2 = os.path.join("data/raw", "us-states.json")

###### takes the appropriate dataframes and saves them into objects for building choropleths:

# State level data:
state_fips = pd.read_csv(IN_PATH_2, dtype={"FIPS": str})
with open(IN_PATH_JSON_2) as response:
    states = json.load(response)

# County level data:
county_fips = pd.read_csv(IN_PATH, dtype={"FIPS": str})
with open(IN_PATH_JSON) as response:
    counties = json.load(response)

###### Making app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(
    [
        html.Div([dcc.Graph(id="the_graph")]),
        html.Div(
            [
                dcc.Input(id="input_state", type="text", value="USA", required=True),
                html.Button(id="go_button", n_clicks=0, children="LETS GOOOO"),
                html.Div(id="output_state"),
            ],
            style={"text-align": "center"},
        ),
    ]
)


@app.callback(
    [
        Output("output_state", "children"),
        Output(component_id="the_graph", component_property="figure"),
    ],
    [Input(component_id="go_button", component_property="n_clicks")],
    [State(component_id="input_state", component_property="value")],
)
def update_output(num_clicks, val_selected):
    if val_selected is None:
        raise PreventUpdate
    if val_selected == "USA":  # Country wide choropleth
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
            hoverlabel=dict(bgcolor="black", font_size=16, font_family="Rockwell"),
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
        )
        return (
            "Type in a state name above to retrieve county level data!",
            fig,
        )
    else:  # County wide choropleth
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
            hoverlabel=dict(bgcolor="black", font_size=16, font_family="Rockwell"),
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
        )
        return (
            "Cool right!? Try another one :)",
            fig,
        )


if __name__ == "__main__":
    app.run_server(debug=True)
# # create exception-handling variables
# states_list = county_fips['STNAME'].unique()
# # print(states_list)

# # prompts the user to type in a state
# state = input("Enter a state name with uppercase first letter: ")
# state = state.title()

# # shows choropleth and handles exceptions if state isn't valid
# if state in states_list:
#     show_state(state)
# elif state == "end":
#     print("Have a great day!")
# else:
#     print("You have not entered a valid State. Please rerun the program, thank you.")
