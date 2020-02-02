# -*- coding: utf-8 
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from shapely import wkt
from shapely.geometry import Polygon, Point
import geopandas as gpd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

url = 'https://raw.githubusercontent.com/ecooper9890/my_insight_app/master/APP_DATA.csv'

df = pd.read_csv(url, error_bad_lines=False)
NYC_county = gpd.read_file('NYC.shp')



boros = ["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title='NYC Lead Water Service Lines'

app.layout = html.Div(children=[
    html.H1(children='New York City Lead Service Line Locator'),

    html.Div(children='''
        
    '''),
    html.Label(["Select Service Line Material:", dcc.RadioItems(id="service",options=[{'label': 'Lead Service Line', 'value': 'Lead'},{'label': 'Non-Lead Service Line', 'value': 'No Lead'}], labelStyle={'display': 'inline-block'})]),	
    html.Label(["Select Borough:", dcc.RadioItems(id="boro",options=[{'label': i, 'value': i} for i in boros],labelStyle={'display': 'inline-block'})]),
    html.Label(["Select Zip Code:",dcc.Dropdown(id="zip")]),
    html.Label(["Select Your Street Address:",dcc.Dropdown(id="staddr")]),
    html.Div(id='prediction')
])


#@app.callback(
#    dash.dependencies.Output("boro", "options"),
#    [dash.dependencies.Input("service","value")],
#)
#def update_options(value):
#    if (value == 'Non Lead'): df_service = df[df['Prediction']==0]
#    if (value == 'Lead'): df_service = df[df['Prediction']==1]
#    return [{'label': i, 'value': i} for i in boros]


@app.callback(
    dash.dependencies.Output("zip", "options"),
    [dash.dependencies.Input("boro","value"), dash.dependencies.Input("service","value")],
)
def update_options(value1,value2):
    if (value2 == 'No Lead'): df_service = df[df['Prediction']==0]
    else: df_service = df[df['Prediction']==1]
    return [{'label': i , 'value': i} for i in df_service[df_service['Borough']==value1]['zip'].unique()]

@app.callback(
    dash.dependencies.Output("staddr", "options"),
    [dash.dependencies.Input("zip","value"),dash.dependencies.Input(component_id = 'service',component_property = "value")],
)
def update_options(value1, value2):
    if (value2 == 'No Lead'): df_service = df[df['Prediction']==0]
    else: df_service = df[df['Prediction']==1]
    return [{'label': i , 'value': i} for i in df_service[df_service['zip']==value1]['Address'].unique()]

@app.callback(
    dash.dependencies.Output(component_id='prediction', component_property='children'),
    [dash.dependencies.Input(component_id='staddr', component_property='value'),dash.dependencies.Input(component_id='service', component_property='value')]
)
def update_output_div(input_value1,input_value2):
    if isinstance(input_value1, type(None)): return ['']
    if (input_value2 == 'No Lead'): a=0
    else: a=1
    if (input_value2 == 'Non Lead'): df_service = df[df['Prediction']==0]
    else: df_service = df[df['Prediction']==1]
    if (input_value1 not in list(df[df['Prediction']==a].Address)): return[' ']
    return ['This address is predicted to have service line of type: ' + input_value2]	
    #p = list(df_service[df_service['Address']==input_value1]['Prediction'])[0]
    #if p==0: return ['This address is predicted to have: NOT LEAD']
    #if p==1: return ['This address is predicted to have: LEAD']    

if __name__ == '__main__':
    app.run_server(debug=True)
