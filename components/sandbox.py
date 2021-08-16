from server import app

import dash
import dash_bootstrap_components as dbc
import dash_trich_components as dtc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction, MATCH, ALL, ALLSMALLER
from dash.exceptions import PreventUpdate

import pandas as pd
from pymongo import MongoClient

import visdcc

from decouple import config

import glob
import json
import random 
import os
import string 
from datetime import datetime


fpath = "json"

db = config("MONGODB_DATABASE")
collection = config("MONGODB_LAYOUT_COLLECTIONS")

# Checks if path is a directory
isDirectory = os.path.isdir(fpath)

if not isDirectory:
    try:
        os.mkdir(fpath)
    except OSError as error:  
        print(error)


# function to generate random IDs
def gen_random_id(total_strings):
    random_id = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k = total_strings))
    return random_id


def utc_now():
    return datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S')

# Function to instantiate the mongoDB to the CRUD of the dashboard
def mongodb_connection(db_name, collection_name):

    mongodb_database = config("MONGODB_ID_CLIENT")

    client = MongoClient(str(mongodb_database))

    db = client[db_name]
    collection = db[collection_name]

    return collection


widgets_name = {"metric1": 'Year Results', "metric2":'Market Share', "metric3":'Costs&Revenue', "monthly_metric3":'Sales Metrics'}

select = html.Div(dbc.Select(
    id="select-widget",
    options=[
        {"label":i[1], "value":i[0]} for i in widgets_name.items()
    ],
    className="bottom8"
))

widget_title = dbc.FormGroup(
    [
        dbc.Label("Widget Title:", html_for="adding-title"),
        dbc.Input(
            type="text",
            id="adding-title",
            placeholder="Type title",
        )
    ]
)

radioitems = dbc.FormGroup(
    [
        dbc.Label("Choose Interval"),
        dbc.RadioItems(
            options=[{'value': i[1], 'label':i[0]} \
                         for i in {'1h':60, '4h':240, '12h':720, 'Daily':1440 }.items()],
            value=60,
            inline=True, 
            id="radioitems-input",
        ),
    ]
)

# Alert component of the Save
widget_add_alert = dbc.Alert(
            "You can't have empty fields. Please fill all the parameters and try again.",
            id="alert-empty-add",
            is_open=False,
            color="danger", className="font-xs",
            duration=3500)


select_chart_type = html.Div(dbc.Select(
    id="select-chart-type",
    options=[
        {"label":i.capitalize(), "value":i} for i in ["bar", "line", "scatter"]
    ],
    # value="bar"
    className="bottom8"
    ))


add_new_chart_modal = html.Div(dbc.Modal(
            [
                dbc.ModalHeader("Add your chart to the dashboard;"),
                dbc.ModalBody(
                    [
                        html.Div([
                            html.Div([widget_title]),
                            html.Div([radioitems]),
                            dbc.Row([dbc.Col([html.Div("Select the Widget: "), select], lg=6),
                                     dbc.Col([html.Div("Chart Type: "), select_chart_type], lg=6)]),
                            widget_add_alert,
                            dbc.Button("Add Widget", 
                                        id="add-widget-dashboard", 
                                        style={"width": "120px"},
                                        className="top8 sandboxBtnColors")
                        ])

                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="add-close",
                               className="ml-auto sandboxBtnColors")
                ),
            ],
            id="modal-add"))



def dynamic_modal_component(id_val, style_button):

    options = ['title', 'interval', 'widget']
    prefix_modal_opt = ['modal']

    modal = html.Div(
        [
            html.Div(dbc.Button(html.I(className="fas fa-cog textColor"),
                     id={"type":"btn-settings", "index":id_val}, 
                                style=style_button), 
                        id=f"settings-{id_val}", style={"width": "20px"}),
                        
            dbc.Modal(
                [
                    dbc.ModalHeader(f"Config of widget ID-{id_val[:5]}"),
                    dbc.ModalBody(
                        [
                            html.Div(["Widget Title: ", dbc.Input(id={"type": "title-opt", "index": id_val}, type="text")]),
                            html.Div(["Widget Interval: ", dcc.Dropdown(id={"type": "interval-opt", "index": id_val})]),
                            html.Div(["Widget Type: ", dcc.Dropdown(id={"type": "widget-type-opt", "index": id_val})]),
                            html.Div(["Chart Type: ", dcc.Dropdown(id={"type": "chart-type-opt", "index": id_val})]),
                            dbc.Button("Save", id={"type":"save-widget-config", "index":id_val})
                        ]
                    ),
                    dbc.ModalFooter(
                        dbc.Button("Close", id={"type":"close-config", "index":id_val}, className="ml-auto")
                    ),
                ],
                id={"type":"modal-config", "index":id_val},
            ),
        ]
    )

    return modal


# This function will create the draggable components inside the responsive-grid-layout
def creating_new_components(id_new, new_title, interval_value, widget_type, chart_type):

    style = { 'border': 'dashed 2px darkgreen' }

    # chart_type = random.choice(["bar", "line", "scatter"])

    close_button_style={"background": "transparent", "border": "none", 
                        "fontSize": "12px", "padding": "0px", 
                        "width": "100%", "color":"transparent"}

    content = html.Div(children=[
        dcc.Store(id={"type": "widget-features", "index":id_new}, 
                  data={"widget_type": widget_type, "chart_type":chart_type, \
                        "interval": interval_value, "title": new_title,\
                        "id":id_new}),
        
        html.Div([
            dcc.Graph(
                id={"type": "graph", "index":id_new},
                figure={
                    'data':
                    [
                        {'x': ['a', 'b', 'c'], 'y': [4, 1, 2], 'type': chart_type, 'name': random.choice(['Brazil', 'US', 'Australia', 'Nigeria', 'China', 'India'])},
                        {'x': ['a', 'b', 'c'], 'y': [2, 4, 5], 'type': chart_type, 'name': random.choice(['Argentina', 'Cuba', 'Russia', 'France', 'Spain'])},
                    ],
                    'layout': 
                    {
                        'title': new_title + " " + str(interval_value),
                        'autosize': True
                    }
                },
                config={
                        'autosizable': True,
                        'doubleClick': 'autosize',
                        'frameMargins': 0},
                style={"margin": "8px 4px 0 4px", "width":"100%"}),
                
            html.Div([
                html.Div(dbc.Button(html.I(className="far fa-hand-paper textColor MyDragHandleClassName"),
                                id={"type":"drag-btn", "index":id_new}, 
                                style=close_button_style, className="dragButton"), 
                        id=f"div-hand-{id_new}", style={"width": "20px"}),
                dbc.Tooltip([html.Div(["Drag the chart."], className="font-xs", 
                                style={ 'color':'lightgrey'})], target=f"div-hand-{id_new}"),
                html.Div(dbc.Button(html.I(className="far fa-window-close red"),
                                id={"type":"btn-close", "index":id_new}, 
                                style=close_button_style),
                        id=f"close-{id_new}", style={"width": "20px"}),
                dbc.Tooltip([html.Div(["Click to close this chart"], 
                             className="font-xs", style={ 'color':'lightgrey'})], 
                            target=f"close-{id_new}"),
                dynamic_modal_component(id_new, style_button=close_button_style),
                dbc.Tooltip([html.Div(["Click to modify parameters."], className="font-xs", style={ 'color':'lightgrey'})], 
                            target=f"settings-{id_new}")
            ], className="displayFlex", style={"marginLeft":"4px"})
    ], style={"border":"solid .1px lightgrey"}, className="width-100")], 
    id=f'{id_new}')
    
    return content


def compare_dict(d1, d2):

    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    shared_keys = d1_keys.intersection(d2_keys)

    # Getting the difference s
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
    same = set(o for o in shared_keys if d1[o] == d2[o])

    return added, removed, modified, same


# Remove the layout of the removed Responsive GridItem
def remove_layout(layout, id_val):
    for i in layout:
        layout[i] = [i for i in layout[i] if i['i'] != id_val]
    return layout


# Alert component of the Save
save_alert = dbc.Alert(
            "You can't save an empty dashboard or an untitled view. Please fix the errors and try again.",
            id="alert-empty-save",
            is_open=False,
            color="danger", className="font-xs",
            duration=3500)

# Modal to save Layout component
modal_save_layout =  html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("Save the layout"),
                dbc.ModalBody(
                    [
                        dbc.Label("Dashboard Name: "),
                        dbc.Input(id="dashboard-save-name", placeholder="Dashboard Name", type="text"),
                        dbc.FormText("Type the name of the Dashboard them click in save."),
                        save_alert,
                        dbc.Button("Save", id="btn-save-layout", className="ml-auto top8 sandboxBtnColors")
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-save", className="ml-auto sandboxBtnColors")
                ),
            ],
            id="modal-save",
        )
    ])


# Alert component of the Save
restore_alert = dbc.Alert(
            "You need to select one layout to be restored.",
            id="alert-empty-restore",
            is_open=False,
            color="danger", className="font-xs top8",
            duration=3500)


# Modal Restore Dashboard
modal_restore_layout =  html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("Load an salved layout."),
                dbc.ModalBody(
                    [
                        dbc.Label("Select the desired report: "),
                        dcc.Dropdown(id='restore-dropdown'),
                        restore_alert,
                        dbc.Button("Load", id="btn-restore-layout", className="ml-auto top8 sandboxBtnColors")
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-restore", className="ml-auto sandboxBtnColors")
                ),
            ],
            id="modal-restore",
        )
    ])



def SandBoxLayout():

    """

        This function build the sandbox component structure.

    """

    layouts = {
    'lg': [],
    'md': [],
    'sm': [],
    'xs': [],
    'xxs':[]
    }

    style = { 'border': 'dashed .5px darkgreen', 'height': '100%' }
    cols = {'lg': 12, 'md':10, 'sm': 6, 'xs': 4, 'xxs': 2}
    breakpoints = {'lg': 1028,  'md':996, 'sm': 768, 'xs': 480 , 'xxs': 0}
    row_height=30

    sandbox_structure = html.Div(
        [
            html.Div(
                [
                    
                   
                    dcc.Store(id="loaded", # storage_type='local',
                              data={"HasModifications": False, "layout_id": None,
                                    "children_structure": None,
                                    'layout_structure': None, "layout_name": None,
                                     "created_at": None, "last_modification":None}),
                    html.Div(id="resize-validation"),
                    visdcc.Run_js(id='javascript'),
                    dbc.Button(html.Div([html.I(className="fa fa-plus"), "  New Chart"], className="font-sm"), 
                                    id="btn-add-chart", n_clicks=0, className="sandboxBtnColors", style={"marginRight":"5px"}),
                    dbc.Tooltip("Click on the Button to add new charts to the application. You have a limitation of X charts.",
                                target="btn-add-chart"),
                    add_new_chart_modal,
                    dbc.Button(html.Div([html.I(className="far fa-times-circle"), "  Reset"], className="font-sm"), 
                                    id="btn-reset-chart", n_clicks=0, className="sandboxBtnColors", style={"marginRight":"5px"}),
                    dbc.Tooltip("Click on the Button to clean all charts in the dashboard.",
                                target="btn-reset-chart"),
                    dbc.Button(html.Div([html.I(className="far fa-save"), "  Save"], className="font-sm"), 
                                    id="open-save", className="sandboxBtnColors", style={"marginRight":"5px"}),
                    modal_save_layout,
                    dbc.Tooltip("Click on the Button to save the dashboard layout.",
                                target="open-save"),
                    dbc.Button(html.Div([html.I(className="far fa-window-restore"), "  Load"], className="font-sm"), 
                                    id="open-restore", className="sandboxBtnColors", style={"marginRight":"5px"}),
                    modal_restore_layout,
                    dbc.Tooltip("Click on the Button to load saved dashboards.",
                                target="open-restore"),
                    dbc.Button(html.Div([html.I(className="far fa-window-restore"), "  Update"], className="font-sm"), 
                                    id="update-restored", className="sandboxBtnColors", style={"marginRight":"5px", "display":"none"}),
                    modal_restore_layout,
                    dbc.Tooltip("Click on the Button to load saved dashboards.",
                                target="update-restored")
                ], className="bottom16", style={ "display":"flex"}),
            html.Div([
                html.Div(
                    [
                        html.Div(["Dashboard Name: ", 
                                  html.Span(id="layout-name", children=["Untitled"],  className="font-lg"),
                                  html.Span(id="layout-info", children=[html.I(className="far fa-question-circle")],  style={"paddingLeft":"5px"}, className="font-md"),
                                  dbc.Tooltip("You're working in an unsaved Dashboard layout.",
                                              target="layout-info", id="tooltip-layout-info")
                        ] #, style={ "display":"flex"} 
                        )
                    ], id="dashboard-name-title", className="textColor"), 
                html.Div(
                    [
                                html.Div(children=[html.Div(["Last Modification: ", 
                                                            html.Span(id="last-mod-at",  
                                                                       # className="fonS"
                                                                        ),
                                                    ], style={"fontSize":"12px"})],
                                        style={"display": "none"}, id="modification-at", className="textColor")]), 
                      html.Div(children=["You can click on Update to save the modifications."], 
                               id="update-alert", className=" font-xs alertMessageColor",
                               style={"display": "none"})], className="bottom8"),
            html.Div(id="loaded-status"),
            dtc.ResponsiveGrid(
                [],
                id='grid-layout',
                cols=cols, 
                breakpoints=breakpoints,  
                layouts=layouts,
                rowHeight=row_height,
                maxRows=45,
                autoSize=True,
                isResizable=True,
                preventCollision=False,
                verticalCompact=True,  
                draggableHandle=".MyDragHandleClassName",
                containerPadding= [15,30],
                margin=[5,20], 
                className="ResponsiveStyle grid-line")
        ], style={"width":"100%", "minHeight":"75vh", 
                  "margin": "32px auto 0", "paddingBottom":"32px"})

    return sandbox_structure


# Will force the content to re-render to fit container width when size changes
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='resize'
    ),
    Output('resize-validation', 'children'),
    [Input('grid-layout', 'layouts'), 
     Input('sidebar-toggle', 'n_clicks')])

# Main callback related to the dashboard engine
# - It will update the layouts and children
# - Save and Store dashboards
# - Reset the component when clicked
@app.callback(
    [Output('grid-layout', 'children'),
     Output('grid-layout', 'layouts'),
     Output('loaded', 'data'),
     Output('dashboard-save-name', 'value')],
    [Input('add-widget-dashboard', 'n_clicks'),
     Input('btn-reset-chart', 'n_clicks'),
     Input('btn-restore-layout', 'n_clicks'),
     Input('btn-save-layout', 'n_clicks'),
     Input({'type': 'btn-close', 'index': ALL}, 'n_clicks'),
     Input("update-restored", 'n_clicks')],
    [State('grid-layout', 'layouts'), 
     State('grid-layout', "children"),
     State('dashboard-save-name', "value"),
     State('restore-dropdown', 'value'), 
     State('adding-title', 'value'),
     State('select-widget', 'value'),
     State('select-chart-type', 'value'),
     State('radioitems-input', 'label'),
     State('radioitems-input', 'value'),
     State('loaded', 'data')])
def myfunc(n_clicks_add,\
           n_clicks_reset, btn_restore, btn_save, btn_close, save_updates,\
           layout, children, name_dashboard, name_restore_report,\
           widget_title, widget_type, chart_type_value, interval_label, interval_value,\
           isLoaded):

    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    # Test the clicked 
    if clicked == 'add-widget-dashboard':
 
        if not all([widget_type, chart_type_value, widget_title]):
            raise PreventUpdate
        else:
            pass

        new_id = gen_random_id(20)

        # widget_title = f"chart-{n_clicks_add}" if widget_title == None or widget_title == [] else widget_title
        #         'title': f'Dash Data Visualization<br>CHART {new_title}',
        condition1 = widget_title == None or widget_title == []
        widget_title = f'Visualization<br>CHART {n_clicks_add}' if condition1 else widget_title

        layout["lg"].append({'i': new_id,
                             'w': 4, 'h': 6, 'x': 0, 'y': (len(children)+1)*5*2, 
                             'maxH':12, 'minH':5, 'minW':3, 'maxW':12,
                             'isDraggable': True, 
                             'isResizable':True, 
                             'isBounded':True})

        layout["md"].append({'i': new_id,
                             'w': 3, 'h': 5, 'x': 0, 'y': (len(children)+1)*5*2, 
                             'maxH':10, 'minH':5, 'minW':3, 'maxW':12,                            
                             'isDraggable': True,  
                             'isResizable':True, 
                             'isBounded':True})

        layout["sm"].append({'i': new_id,
                             'w': 3, 'h': 6, 'x': 0, 'y': (len(children)+1)*5*2,  
                             'maxH':10, 'minH':4, 'minW':2, 'maxW':6,                            
                             'isBounded':True, 
                             'isResizable':True, 
                             'isDraggable': True})

        layout["xs"].append({'i': new_id,
                             'w': 2, 'h': 6, 'x': 0, 'y': (len(children)+1)*5*2,  
                             'maxH':10, 'minH':6, 'minW':2, 'maxW':4,                              
                             'isBounded':True, 
                             'isResizable':True, 
                             'isDraggable': True})

        layout["xxs"].append({'i': new_id,
                             'w': 2, 'h': 6, 'x': 0, 'y': (len(children)+1)*5*2,  
                             'maxH':8, 'minH':5, 'minW':1, 'maxW':2,                              
                             'isBounded':True, 
                             'isResizable':True, 
                             'isDraggable': True})

        return children + [creating_new_components(new_id, widget_title, interval_value, \
                                                   widget_type, chart_type_value)], \
            layout, isLoaded, dash.no_update

    # it will not have effects in the layout, 
    # but it will save the children + layouts on MongoDB
    elif clicked == 'btn-save-layout':

        if ((name_dashboard == None) or ((children == []) and (layout == {'lg':[], 'md':[] , 'sm': [], 'xs':[], 'xxs':[]}))): 
            raise PreventUpdate

        else:
            
            N = 7
            random_id = gen_random_id(N)

            filename = name_dashboard if not None else f"state_saved_{random_id}"
            username="user1-test" 
            created_date= utc_now()
            # defining the 
            json_final = {"layout_id":random_id,
                          "layout_alias": filename,
                          "created_by": username,
                          "user": username, 
                          "created_at":created_date,
                          "last_modification":created_date,
                          "content": [
                            {
                                "layout": layout, 
                                "children": children
                            }
                        ]
                    }

            ## receive the mongodb instance and insert the new dashboard value
            coll = mongodb_connection(db, collection)

            coll.insert_one(json_final)
            
            return children, layout, \
                {"HasModifications": True, 
                 "layout_id": random_id,  
                 "children_structure": json_final["content"][0]["children"], 
                 "layout_structure": json_final["content"][0]["layout"], "layout_name": filename, 
                 "created_at": json_final['created_at'], 
                 "last_modification":json_final['last_modification']}, None

    elif clicked == 'btn-restore-layout':
        
        if name_restore_report is None: 
            raise PreventUpdate
        else: 
            pass
        
        coll = mongodb_connection(db, collection)
 
        result = coll.find_one({"layout_id": name_restore_report})

        loaded_layout = result['content'][0]['layout']
        loaded_children = result['content'][0]['children']

        created_date = result['created_at']
        last_modification_date = result['last_modification']

        return loaded_children, loaded_layout, \
            {"HasModifications": True, "layout_id": name_restore_report,
             "children_structure": loaded_children,'layout_structure': loaded_layout, 
             "layout_name": result['layout_alias'], 
             "created_at": created_date, "last_modification": last_modification_date}, \
                 dash.no_update

    elif clicked == 'btn-reset-chart':

        return [], {'lg':[], 'md':[] , 'sm': [], 'xs':[], 'xxs':[]}, \
            {"HasModifications": False, "layout_id": None,
             "children_structure": None,'layout_structure': None, 
             "layout_name": None, 
             "created_at": None, "last_modification": None}, \
                 dash.no_update

    elif clicked == 'update-restored':

        if isLoaded['layout_id'] is None: 
            raise PreventUpdate
        else: 
            pass

        coll = mongodb_connection(db, collection)
        # coll.insert_one(json_final)

        last_updated= utc_now()

        update_mongo_db = coll.update_one({"layout_id": isLoaded['layout_id']}, 
                                 {"$set":{"content.0.layout": layout,
                                          "content.0.children": children, 
                                          "last_modification": last_updated}})

        return children, layout, \
               {"HasModifications": True, "layout_id": isLoaded['layout_id'], 
                "children_structure": children,
                'layout_structure': layout, 
                "layout_name": isLoaded['layout_name'],
                "created_at": isLoaded['created_at'], 
                "last_modification": last_updated}, dash.no_update

    ## It's to remove the widgets through the "close" button
    else:
        # Transforming to dict
        clicked = eval(clicked)

        # Remove the children that was clicked to close
        children = [vals for vals in children if vals['props']['id'] != clicked['index']]

        # Removing the layout that was clicked to close
        layout = remove_layout(layout, clicked['index'])

        return children, layout, isLoaded, dash.no_update


@app.callback(
    Output("layout-name", "children"),
    Output("last-mod-at", "children"),
    Output('update-alert', 'children'),
    Output('tooltip-layout-info', 'children'),
    Input('loaded', 'data'))
def loaded_status(isLoaded):

    if isLoaded == None:
        return "Untitled", \
               "-", \
               "Click in Update button to save the modifications.", \
               "Click on Load to restore a Layout or save a new Dashboard layout"

    elif isLoaded['HasModifications']:
        return f"{isLoaded['layout_name']}", \
               f"{isLoaded['last_modification']}", \
               "Click in Update button to save the modifications.", \
               f"The layout was created at {isLoaded['created_at']}."

    else:
        return "Untitled", \
               "-", \
               "Click in Update button to save the modifications.", \
               "Click on Load to restore a Layout or save a new Dashboard layout"


@app.callback(
    Output("update-restored", "style"),
    Output('update-alert', 'style'),
    Input('loaded', 'data'),
    Input('grid-layout', 'layouts'),
    Input('grid-layout', 'children'),
    Input("update-restored", "style"),
    Input('update-alert', 'style'),
    Input({'type': 'widget-features', 'index': ALL}, "data")
    )
def loaded_status(isLoaded, layout, children, component_style, update_alert, data):

    if (isLoaded == None) or (isLoaded == None and component_style['display'] == 'grid'):
        raise PreventUpdate

    elif isLoaded:
        if isLoaded["HasModifications"]:

            layout_added, layout_removed,\
                 layout_modified, layout_same = compare_dict(isLoaded['layout_structure'], layout)

            modification_children = [child["props"]['children'][0]['props']['data'] for child in isLoaded['children_structure']]
            
            children_isDifferent = modification_children != data

            if (layout_modified != {} or children_isDifferent):
                return {"display":"grid"}, {"display":"grid"}
            else:
                return {"display":"none"}, {"display":"none"}
        else:
            return  {"display":"none"}, {"display":"none"}
    else:
        return  {"display":"none"}, {"display":"none"}


@app.callback(
     Output({'type': 'modal-config', 'index': MATCH}, "is_open"),
    [Input({'type': 'btn-settings', 'index': MATCH}, "n_clicks"),
     Input({'type': 'close-config', 'index': MATCH}, "n_clicks"),
     Input({"type":"save-widget-config", 'index': MATCH}, "n_clicks")],
    [State({'type': 'modal-config', 'index': MATCH}, "is_open")],
)
def config_modal_trigger(n1, n2, id_val, is_open):

    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        pass

    clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
     Output({'type': "title-opt", 'index': MATCH}, "value"),
     Output({'type': "interval-opt", 'index': MATCH}, "value"),
     Output({'type': "interval-opt", 'index': MATCH}, "options"),
     Output({'type': "widget-type-opt", 'index': MATCH}, "options"),
     Output({'type': "widget-type-opt", 'index': MATCH}, "value"),
     Output({'type': "chart-type-opt", 'index': MATCH}, "value"),
     Output({'type': "chart-type-opt", 'index': MATCH}, "options"),
    [Input({'type': 'btn-settings', 'index': MATCH}, "n_clicks")],
    [State({'type': 'widget-features', 'index': MATCH}, "data"),
     State("radioitems-input", "options"),
     State("select-widget", "options"), 
     State('select-chart-type', 'options')]
)
def config_modal_trigger(n_clicks, features, interval_opts, widget_opts, chart_opts):

    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        pass

    clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    return features['title'], features['interval'], interval_opts, \
            widget_opts, features['widget_type'], \
                features["chart_type"], chart_opts


@app.callback(
    Output('modification-at', 'style'),
    Input('loaded', 'data'))
def loaded_status(isLoaded):

    if isLoaded["HasModifications"]:
        return {"display":"grid"} #, {"display":"grid"}
    else: 
        return {"display":"none"} #,  {"display":"none"}


# Output("create-new-dashboard",  "n_clicks")
# Input("create-new-dashboard",  "n_clicks")
# Input("load-dashboards",  "n_clicks")




# callback of the alert component in the save modal
@app.callback(
    Output("alert-empty-save", "is_open"),
    [Input("btn-save-layout", "n_clicks")],
    [State("alert-empty-save", "is_open"),
     State('dashboard-save-name', 'value'),
     State('grid-layout', 'children')],
)
def toggle_alert_save(n, is_open, name_value, children):

    if name_value == "" or name_value is None or children == []:
        pass
    else:
        raise PreventUpdate

    if n:
        return not is_open
    return is_open


@app.callback(
     Output({'type': 'widget-features', 'index': MATCH}, "data"),
     Output({"type": "graph", 'index': MATCH}, "figure"),
    [Input({"type":"save-widget-config", "index":MATCH}, "n_clicks")],
    [State({'type': "title-opt", 'index': MATCH}, "value"),
     State({'type': "interval-opt", 'index': MATCH}, "value"),
     State({'type': "widget-type-opt", 'index': MATCH}, "value"), 
     State({'type': 'widget-features', 'index': MATCH}, "data"),
     State({"type": "graph", 'index': MATCH}, "figure"),
     State({"type": "chart-type-opt", 'index': MATCH}, "value")])
def change_internal_config(n_clicks, title, interval, \
                           widget_type, data, 
                           chart_figure, new_chart_type):

    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    if not all([title, interval, widget_type, new_chart_type]):
        raise PreventUpdate
    else: 
        pass
 
    updated_values = zip(['title', 'interval', 'widget_type', 'chart_type'], [title, interval, widget_type, new_chart_type])

    for key, val in updated_values:
        data[key] = val

    for i in chart_figure['data']:
        i['type'] = new_chart_type

    # print(chart_figure)
    chart_figure['layout']['title']['text'] = title + " " + str(interval)

    return data, chart_figure


# callback of the alert component in the save modal
@app.callback(
    Output("alert-empty-add", "is_open"),
    [Input("add-widget-dashboard", "n_clicks")],
    [State("alert-empty-add", "is_open"),
     State('select-widget', 'value'),
     State('select-chart-type', 'value'),
     State('adding-title', 'value')],
)
def toggle_alert_add(n, is_open, widget_type, \
                     chart_type_value, widget_title):

    if all([widget_type, chart_type_value, widget_title]):
        raise PreventUpdate
    else:
        pass

    # if widget_type is None:
    #     pass
    # else:
    #     raise PreventUpdate

    if n:
        return not is_open
    return is_open





# Callback related to SAVE MODAL component
@app.callback(
    Output("modal-save", "is_open"),
    [Input("open-save", "n_clicks"), 
     Input("close-save", "n_clicks"), 
     Input("btn-save-layout", "n_clicks")],
    [State("modal-save", "is_open"),
     State('dashboard-save-name', 'value'),
     State("grid-layout", "layouts")])
def toggle_modal(n1, n2, closing, is_open, name_value, layout):

    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        pass

    clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    # Avoid to save empty dashboards and untitled layouts
    if clicked == "open-save" or clicked == "btn-save-layout":
        if ((is_open == True) and ((name_value == "") or (name_value is None))):
            raise PreventUpdate
        else:
            if layout == {'lg':[], 'md':[] , 'sm': [], 'xs':[], 'xxs':[]} and is_open == True: 
                raise PreventUpdate
            else:
                # If it's everything filled correctly, it will open or close the modal
                if n1 or n2 or closing:
                    return not is_open
                return is_open

    # if clicking in the close button - it will run the code below
    else:
        if n1 or n2 or closing:
            return not is_open
        return is_open


# Callback of the modal of restore
@app.callback(
    Output("modal-restore", "is_open"),
    [Input("open-restore", "n_clicks"), 
     Input("close-restore", "n_clicks"), 
     Input("btn-restore-layout", "n_clicks")],
    [State("modal-restore", "is_open"),
     State('restore-dropdown', 'value')],
)
def toggle_modal(n1, n2, closing, is_open, restore_layout_name):

    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    # Test if restore isn't None;
    # If it's null it will not update the component
    if clicked == "btn-restore-layout" and restore_layout_name is None: 
        raise PreventUpdate
    else:
        if n1 or n2 or closing:
            return not is_open
        return is_open


# Callback of the modal of restore
@app.callback(
    Output('restore-dropdown', 'value'),
    [Input("btn-restore-layout", "n_clicks")],
    [State('restore-dropdown', 'value')],
)
def toggle_modal(btn_restore, restore_name):

    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    # Test if restore isn't None;
    # If it's null it will not update the component
    if clicked == "btn-restore-layout" and restore_name is None: 
        raise PreventUpdate
    else:
        return None


# callback of the alert component in the restore modal
@app.callback(
    Output("alert-empty-restore", "is_open"),
    Input("btn-restore-layout", "n_clicks"),
    [State("alert-empty-restore", "is_open"),
     State('restore-dropdown', 'value')]
)
def toggle_alert_restore(n, is_open, restore_val):

    if restore_val == "" or restore_val is None:
        pass
    else:
        raise PreventUpdate

    if n:
        return not is_open
    return is_open


# Callback of the modal of add
@app.callback(
    Output("modal-add", "is_open"),
    [Input("btn-add-chart", "n_clicks"), 
     Input("add-close", "n_clicks"), 
     Input("add-widget-dashboard", "n_clicks")],
    [State("modal-add", "is_open"),
     State('select-widget', 'value'),
     State('adding-title', 'value'),
     State('select-chart-type', 'value')],
)
def toggle_modal_add(n1, n2, closing, is_open, 
                     widget_type, widget_title, new_chart_type):

    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    # if not all([title, interval, widget_type, new_chart_type])
    # # Test if restore isn't None;
    # # If it's null it will not update the component
    if not all([widget_title, widget_type, new_chart_type]) and clicked == "add-widget-dashboard": 
        raise PreventUpdate

    # if all conditions aren't fitted it will run the code below
    else:
        if n1 or n2 or closing:
            return not is_open
        return is_open


# Get all dashboards available to load 
@app.callback(
    Output('restore-dropdown', "options"),
    Input("open-restore", "n_clicks")
)
def dropdown_options(n_clicks):

    if n_clicks is None:
        raise PreventUpdate
    else:
        pass

    db = config("MONGODB_DATABASE")
    collection = config("MONGODB_LAYOUT_COLLECTIONS")

    coll = mongodb_connection(db, collection)

    dropdown_options = [{"value": vals['layout_id'],\
                         "label":f"{vals['layout_alias']} - {vals['created_by']}"} \
                             for vals in coll.find({})]

    return dropdown_options


# Clean the add entries when clicking in the add.
@app.callback(
    Output('adding-title', "value"),
    Output("select-widget", "value"),
    Output("select-chart-type", "value"),
    Output("radioitems-input", "value"),
    Input("add-widget-dashboard", "n_clicks"),
    State('adding-title', "value"),
    State("select-widget", "value"),
    State('select-chart-type', 'value')
)
def toggle_modal(n_clicks, widget_title, widget_type, new_chart_type):

    if not all([widget_title, widget_type, new_chart_type]): 
        raise PreventUpdate
    else:
        pass

    return None, None, None, 60

