from server import app

import dash
from dash import html, dcc, Input, Output, State, ClientsideFunction, dash_table
import dash_bootstrap_components as dbc

import pandas as pd

# Dash Utils 
# from dash_extensions import Download
# from dash_extensions.snippets import send_data_frame

# Importing content structure & Sidebar
from components.analytics import AnalyticsLayout
from components.SideBarComponent import sidebar

import json

# this server instance is used on the deployment
server = app.server

### APPLICATION LAYOUT 
app.layout = html.Div([
    html.Div(id='initiating', 
             children=["start-app"], style={"display":"none"}),
    dcc.Location(id="url", refresh=False),
    #content container
    sidebar,
    # Analytics Layout is the main structure of the content
    # page-content have this name because of the responsive sidebar component
    html.Div(AnalyticsLayout, 
              style={'minHeight':"750px"},
              id="page-content")
    ], id="draggable-comp-layout")


@app.callback(
    Output("sidebar", "className"),
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar", "className")]
)
def toggle_classname(n, classname):

    if (n and classname == "") or (n and classname == "bgColor"):
        # print(classname, classname == "")
        return "collapsed"
    return ""


@app.callback(
    Output("collapse", "is_open"),
    [Input("navbar-toggle", "n_clicks")],
    [State("collapse", "is_open")]
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



if __name__ == '__main__':
    app.run_server(debug=True)
