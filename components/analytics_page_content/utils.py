from server import app

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table

import plotly_express as px
import pandas as pd
import plotly.graph_objects as go

from decouple import config

df = px.data.iris()
df2 = pd.read_csv(config("BUCKET_ADDRESS_1"))
df3 = pd.read_csv(config("BUCKET_ADDRESS_2"))


all_dims = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']


fig1 = html.Div([
    dbc.Label("Select the features that you want to plot"),
    dcc.Dropdown(
        id="dropdown",
        options=[{"label": x, "value": x}
                 for x in all_dims],
        value=all_dims[:2],
        multi=True,
        style={"maxWidth":"500px"},
        className="bottom16"
    ),
    dcc.Graph(id="graph-dashboard", className="width-100")
])



fig2 = go.Figure(data=go.Choropleth(
    locations=df2['CODE'],
    z=df2['GDP (BILLIONS)'],
    text=df2['COUNTRY'],
    colorscale='Blues',
    autocolorscale=False,
    reversescale=True,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    colorbar_tickprefix='$',
    colorbar_title='GDP<br>Billions US$',
))

fig2.update_layout(
    title_text='2014 Global GDP',
    autosize=True,
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    ),
    annotations=[dict(
        x=0.55,
        y=0.1,
        xref='paper',
        yref='paper',
        text='Source: <a href="https://www.cia.gov/library/publications/the-world-factbook/fields/2195.html">\
            CIA World Factbook</a>',
        showarrow=False
    )],
    margin=dict(
        l=20,
        r=20,
        b=20,
        t=30,
        pad=0
    )
)


dash_table = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df3.columns],
    data=df3.to_dict('records'),
)

tab1_content = html.Div([
    html.Br(),
    #html.P("This is tab 1!", className="card-text"),
    #dbc.Button("Click here", color="success"),
    fig1
    ], className="width-100")


tab2_content = html.Div(
    [
    #html.P("This is tab 2!", className="card-text"),
    #dbc.Button("Don't click here", color="danger"),
    dcc.Graph(id="world_map", figure=fig2, className="width-100"),
    dash_table], 
    className="width-100")


tabs = dbc.Tabs([
    dbc.Tab(tab1_content, label="Tab 1"),
    dbc.Tab(tab2_content, label="Tab 2"),
    dbc.Tab(
        "This tab's content is never seen", label="Tab 3", disabled=True
    )])



def AnalyticsContent(analytics_option):

    test= {"/analytics-dashboard": tabs}

    return test[analytics_option]



@app.callback(
    Output("graph-dashboard", "figure"),
    [Input("dropdown", "value")])
def update_bar_chart(dims):
    
    fig = px.scatter_matrix(
        df, dimensions=dims, color="species")

    fig.update_layout(autosize=True)

    return fig


    