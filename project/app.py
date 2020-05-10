import sys
import os
import dash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'packages')))

from typing import List, Dict
from packages import data_types
from packages import stock_data_manager
from packages import stock_data_consumer

from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html

sdm = stock_data_manager.StockDataManager()
sdm._testing = True
sdc = stock_data_consumer.StockDataConsumer(all_symbols=[], stock_categories={}, index_tracker_stocks=[], 
                                            watchlist_stocks=[], position_stocks=[], positions=[])

def refresh_data() -> stock_data_consumer.StockDataConsumer:
    sdm.run()
    sdc = stock_data_consumer.StockDataConsumer(all_symbols=sdm.all_symbols, stock_categories=sdm.stock_categories, 
                                            index_tracker_stocks=sdm.index_tracker_stocks, watchlist_stocks=sdm.watchlist_stocks,
                                            position_stocks=sdm.position_stocks, positions=sdm.positions)
    return sdc

sdc = refresh_data()

print('Invested Amount: {}'.format(sdc.calculate_invested_amount()))
print('Market Value: {}'.format(sdc.calculate_market_value()))
print('Unrealized Gain: {}'.format(sdc.calculate_unrealized_gain()))
print('Realized Gain: {}'.format(sdc.realized_gain()))
print('Values for Stock: {}'.format(sdc.values_for_stock(symbol='ARKK', start_date=datetime.fromisoformat('2015-01-01').astimezone(), end_date=datetime.now().astimezone())))
print('Percent Gain DateFrame: {}'.format(sdc.pct_gain_for_stock(symbol='ARKK', start_date=datetime.fromisoformat('2015-01-01').astimezone(), end_date=datetime.now().astimezone())))

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("dash-logo.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "New York Oil and Gas",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Production Overview", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Learn More", id="learn-more-button"),
                            href="https://plot.ly/dash/pricing/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Filter by construction date (or select range in histogram):",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="year_slider",
                            min=1960,
                            max=2017,
                            value=[1990, 2010],
                            className="dcc_control",
                        ),
                        html.P("Filter by well status:", className="control_label"),
                        dcc.RadioItems(
                            id="well_status_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Active only ", "value": "active"},
                                {"label": "Customize ", "value": "custom"},
                            ],
                            value="active",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        # dcc.Dropdown(
                        #     id="well_statuses",
                        #     options=well_status_options,
                        #     multi=True,
                        #     value=list(WELL_STATUSES.keys()),
                        #     className="dcc_control",
                        # ),
                        dcc.Checklist(
                            id="lock_selector",
                            options=[{"label": "Lock camera", "value": "locked"}],
                            className="dcc_control",
                            value=[],
                        ),
                        html.P("Filter by well type:", className="control_label"),
                        dcc.RadioItems(
                            id="well_type_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Productive only ", "value": "productive"},
                                {"label": "Customize ", "value": "custom"},
                            ],
                            value="productive",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        # dcc.Dropdown(
                        #     id="well_types",
                        #     options=well_type_options,
                        #     multi=True,
                        #     value=list(WELL_TYPES.keys()),
                        #     className="dcc_control",
                        # ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="well_text"), html.P("No. of Wells")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="gasText"), html.P("Gas")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="oilText"), html.P("Oil")],
                                    id="oil",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="waterText"), html.P("Water")],
                                    id="water",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="count_graph")],
                            id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="main_graph")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="individual_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="pie_graph")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="aggregate_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

@app.callback(
    [
        Output("gasText", "children"),
        Output("oilText", "children"),
        Output("waterText", "children"),
    ],
    [Input("aggregate_data", "data")],
)
def update_text(data):
    symbols = sdm.get_all_symbols()
    result = adg.calculate_invested_amount()
    return symbols[0] + " mcf", symbols[1] + " bbl", str(result) + " bbl"

if __name__ == '__main__':
    # app.run_server(debug=True)
    exit()
