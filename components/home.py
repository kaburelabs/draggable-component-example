from server import app
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


def HomePageLayout():

    starting_home= html.Div(id="homepage-layout", children=["starting"], style={"display":"none"})

    home = html.Div(
        [
            html.H2("Draggable Component", className="display-4"),
            html.H5("It's simple system based on react-grid-layout component using an very advanced pattern match callback implementation", className="bottom32"),
            html.P("The solution was developed by trich.ai developers", className="lead"),
            html.P(
                "If you're new with Patter-Matching callbacks you can visit the below contents", 
                className="lead bottom32"
            ),
            html.Div([
                html.A("DASH DOCUMENTATION", 
                    href="https://dash.plotly.com/pattern-matching-callbacks", 
                    target="blank", className="bottom16", style={"color":"#007bff"}),
                html.Iframe(width="560", height="315",
                            src="https://www.youtube.com/embed/4gDwKYaA6ww")
            ], style={"display": "grid"})
        ], className="textColor"
    )

    return html.Div([starting_home, home])


    