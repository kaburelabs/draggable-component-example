import dash
import dash_bootstrap_components as dbc

fontAwesome = "https://use.fontawesome.com/releases/v5.15.1/css/all.css"
dashBoostrap = dbc.themes.BOOTSTRAP

# CSS files and links
external_stylesheets = [dbc.themes.BOOTSTRAP,  # adding the bootstrap inside the application
                        fontAwesome
                        ]

app = dash.Dash(__name__, 
                suppress_callback_exceptions=True,
                external_stylesheets=external_stylesheets,
                # prevent_initial_callbacks=True,
                # routes_pathname_prefix='/dash/',
                # It's what make the app be responsive;
                meta_tags=[{
                        "name": "viewport",
                        "content": "width=device-width, initial-scale=1, maximum-scale=1"
                    }])

# allow the app access local css and js scripts
app.css.config.serve_locally = True

# setting the title
app.title = 'Draggable Component'


      