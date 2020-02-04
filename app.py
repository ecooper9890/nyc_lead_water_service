# -*- coding: utf-8 
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
#from shapely import wkt
#from shapely.geometry import Polygon, Point
import geopandas as gpd
import folium
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

url = 'https://raw.githubusercontent.com/eric-r-cooper/my_insight_app/master/APP_DATA.csv'

#df = pd.read_csv(url, error_bad_lines=False)
t1 = pd.read_csv('https://raw.githubusercontent.com/eric-r-cooper/nyc_lead_water_service/master/APP_DATA_address.csv',error_bad_lines=False)
t2 = pd.read_csv('https://raw.githubusercontent.com/eric-r-cooper/nyc_lead_water_service/master/APP_DATA_yr.csv',error_bad_lines=False)
t3 = pd.read_csv('https://raw.githubusercontent.com/eric-r-cooper/nyc_lead_water_service/master/APP_DATA_lat.csv',error_bad_lines=False)
t4 = pd.read_csv('https://raw.githubusercontent.com/eric-r-cooper/nyc_lead_water_service/master/APP_DATA_lon.csv',error_bad_lines=False)
df = t1.merge(t2)
df = df.merge(t3)
df = df.merge(t4)
df.drop(columns=['Unnamed: 0'],inplace=True)

ny_map = folium.Map(location=[40.682, -73.945],tiles='Stamen Toner' ,zoom_start=10)

boros = ["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title='NYC Lead Water Service Lines'



app.layout = html.Div(children=[
    html.H1(children='New York City Lead Service Line Locator'),

    html.Label(["Select Service Line Material:", dcc.RadioItems(id="service",options=[{'label': 'Lead Service Line', 'value': 'Lead'},{'label': 'Non-Lead Service Line', 'value': 'No Lead'}], labelStyle={'display': 'inline-block'})]),	
    html.Label(["Select Borough:", dcc.RadioItems(id="boro",options=[{'label': i, 'value': i} for i in boros],labelStyle={'display': 'inline-block'})]),
    html.Label(["Select Zip Code:",dcc.Dropdown(id="zip")]),
    html.Label(["Select Your Street Address:",dcc.Dropdown(id="staddr")]),
    html.Iframe(id='map', srcDoc=ny_map._repr_html_(), width='50%',height='400',style={'width': '49%', 'display': 'inline-block'}),
    html.Div(id='prediction',style={'width': '49%', 'display': 'inline-block'}),
    #dash_table.DataTable(id='table',columns=[{"name": i, "id": i} for i in df.columns],data=df.head().to_dict('records'),style={'width': '49%', 'display': 'inline-block'}),
    #html.Div([dash_table.DataTable(id='tweet_table', rows=[{}])])    
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
    if (input_value2 == 'No Lead'): df_service = df[df['Prediction']==0]
    else: df_service = df[df['Prediction']==1]
    if (input_value1 not in list(df[df['Prediction']==a].Address)): return[' ']
    return ['This address is predicted to have service line of type: ' + input_value2]	
    #p = list(df_service[df_service['Address']==input_value1]['Prediction'])[0]
    #if p==0: return ['This address is predicted to have: NOT LEAD']
    #if p==1: return ['This address is predicted to have: LEAD']    

@app.callback(
    dash.dependencies.Output(component_id='map', component_property='srcDoc'),
    [dash.dependencies.Input(component_id='staddr', component_property='value'),dash.dependencies.Input(component_id='service', component_property='value')]
)
def update_output_div(input_value1,input_value2):
    if isinstance(input_value1, type(None)): return [folium.Map(location=[40.682, -73.945],tiles='Stamen Toner' ,zoom_start=10)._repr_html_()]
    new_map = folium.Map(location=[40.682, -73.945],tiles='Stamen Toner' ,zoom_start=10)
    lat = df[df['Address']==input_value1].iloc[0]['latitude']
    lon = df[df['Address']==input_value1].iloc[0]['longitude']
    if (df[df['Address']==input_value1].iloc[0]['Prediction'] == 1): marker = folium.Marker(location=[lat, lon],icon=folium.Icon(color='red'))
    else: marker = folium.Marker(location=[lat, lon],icon=folium.Icon(color='blue'))
    marker.add_to(new_map)
    return [new_map._repr_html_()]

if __name__ == '__main__':
    app.run_server(debug=True)
