
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import dash_trich_components as dtc

theme_toggle = dtc.ThemeToggle()


LOGO_PATH = "assets/images/fundo_transp.png"


# we use the Row and Col components to construct the sidebar header
# it consists of a title, and a toggle, the latter is hidden on large screens
sidebar_header = dbc.Row(
    [
        dbc.Col(html.Img(id="logo-src-color",  src=LOGO_PATH,
                         style={"height": "26px"}), 
                         style={"display":"flex", "align-items":"center"}),
        dbc.Col(
            [
                html.Button(
                    # use the Bootstrap navbar-toggler classes to style
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler ToggleSideBarItem",
                    # the navbar-toggler classes don't set color
                    id="navbar-toggle",
                ),
                html.Button(
                    # use the Bootstrap navbar-toggler classes to style
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler ToggleSideBarItem",
                    # the navbar-toggler classes don't set color
                    id="sidebar-toggle",
                ),
            ],
            # the column containing the toggle will be only as wide as the
            # toggle, resulting in the toggle being right aligned
            width="auto",
            # vertically align the toggle in the center
            align="center",
        )])

analytics_href = ['home',  'sandbox', 'settings']
analytics_alias = [" Home", " Sandbox", " Settings"]
awesome_icons = ["fas fa-home", "fas fa-puzzle-piece", "fas fa-cogs"]


sidebar = html.Div(
    [
        sidebar_header,
        # we wrap the horizontal rule and short blurb in a div that can be
        # hidden on a small screen
        html.Div(
            [
                html.Hr(),
                html.P(
                    "Dragglable Component Example",
                    className="lead bottom16 textColor",
                ),
            ],
            id="blurb"
        ),
        # use the Collapse component to animate hiding / revealing links
        dbc.Collapse([
            dbc.Nav(
                ## Create all the buttons to the dashboard
                children=[dbc.Button([html.I(className=i[2]), i[1]], 
                          href=f'/analytics-{i[0]}', className="analyticsBtnColors SBBtnStyle bottom8"
                          ) \
                             for i in zip(analytics_href, analytics_alias, awesome_icons)],
                vertical=True,
                pills=True,
            ),
            # Theme Toggle 
            html.Div(theme_toggle)
            ],
            id="collapse",
        ),
    ],
    id="sidebar", className="bgColor"
)





