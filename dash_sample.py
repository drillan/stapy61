import dash

# from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

gapminder = px.data.gapminder()
continents = gapminder["continent"].unique().tolist()
years = gapminder["year"].unique().tolist()
contries = gapminder.country.unique().tolist()

app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Dropdown(
                    id="continent-dropdown",
                    options=[{"label": c, "value": c} for c in continents],
                    value=continents,
                    multi=True,
                    style={"textAlign": "center"},
                ),
                dcc.Graph(id="scatter"),
                dcc.Slider(
                    id="year-slider",
                    min=gapminder["year"].min(),
                    max=gapminder["year"].max(),
                    value=gapminder["year"].min(),
                    marks={str(year): str(year) for year in years},
                    # marks={str(year): str(year)[2:] for year in years},
                    step=None,
                ),
            ],
            style={"width": "50%", "display": "inline-block", "verticalAlign": "top"},
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id="country-dropdown",
                    options=[{"value": contry, "label": contry} for contry in contries],
                    value=["Japan", "United States"],
                    multi=True,
                ),
                dcc.Graph(id="line"),
            ],
            style={"width": "50%", "display": "inline-block", "verticalAlign": "top"},
        ),
    ]
)


@app.callback(
    Output("scatter", "figure"),
    [Input("year-slider", "value"), Input("continent-dropdown", "value")],
)
def update_scatter(selected_year, selected_continent):
    filtered_df = gapminder[
        (gapminder["year"] == selected_year)
        & gapminder["continent"].isin(selected_continent)
    ]

    if len(filtered_df) == 0:
        fig = px.scatter()
    else:
        fig = px.scatter(
            filtered_df,
            x="gdpPercap",
            y="lifeExp",
            size="pop",
            color="continent",
            hover_name="country",
            log_x=True,
            size_max=55,
        )

    fig.update_layout(transition_duration=500)

    return fig


@app.callback(Output("line", "figure"), [Input("country-dropdown", "value")])
def update_line(selected_country):
    selected_gapminder = gapminder[gapminder["country"].isin(selected_country)]
    return px.line(selected_gapminder, x="year", y="lifeExp", color="country")


if __name__ == "__main__":
    app.run_server(debug=True, port=8052)
    # app.run_server(mode="inline")
