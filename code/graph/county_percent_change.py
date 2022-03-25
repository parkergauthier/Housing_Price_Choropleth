"""After running the 'build' scripts, this script will prompt the user to type in the name of a state.
Once a state is typed in, and the user presses ENTER, a choropleth will display of the state with all of
its counties, colored by percent change from 2010-2019."""

# Import modules
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

# Set paths and directories
IN_PATH = os.path.join("data", "COUNTY_AGGREGATE_FIPS.csv")
IN_PATH_JSON = os.path.join("data", "geojson-counties-fips.json")

# Saves county-level dataframe into an object
county_fips = pd.read_csv(IN_PATH, dtype={"FIPS": str})

# Loads in json data that will tell plotly the corrdinates for counties
with open(IN_PATH_JSON) as response:
    counties = json.load(response)

# Making app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(
    [
        html.Div([dcc.Graph(id="the_graph")]),
        html.Div(
            [
                dcc.Input(
                    id="input_state", type="text", value="Colorado", required=True
                ),
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
    else:
        df = county_fips[county_fips["STNAME"] == val_selected]

        state_change = px.choropleth(
            df,
            geojson=counties,
            locations="FIPS",
            color="New_percent_change",
            color_continuous_scale="PuBu",
            range_color=(0, 100),
            scope="usa",
            labels={"New_percent_change": "Percent Change in Housing Price"},
            title="Percent Change in House Values from 2010-2019 by County",
        )
        state_change.update_geos(fitbounds="locations", visible=False)
        state_change.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return (
            'The input value was "{}" and the button has been \
                clicked {} times'.format(
                val_selected, num_clicks
            ),
            state_change,
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
