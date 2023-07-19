import pandas as pd

# pip install "pymongo[srv]"
#import pymongo

# from bson.objectid import ObjectId
# from datetime import datetime
from dash import Dash, dcc, html, Input, Output, State,dash_table
import dash_bootstrap_components as dbc
#from dash_table import DataTable
import plotly.express as px
from datetime import date  # , datetime

# datetime object containing current date and time


from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://Topaccina:1234@cluster0.uj4bmfd.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)
# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["vegGarden"]
collection = db["harvestTracking"]
selection=db["selection"]


#x = collection.find({}, {"category": "Zucchini"})


df_sel=pd.DataFrame(list(selection.find()))
# Convert id from ObjectId to string so it can be read by DataTable
df_sel['_id'] = df_sel['_id'].astype(str)
df = pd.DataFrame(list(collection.find()))
# Convert id from ObjectId to string so it can be read by DataTable
df['_id'] = df['_id'].astype(str)  
print(df.columns)
df_sum=df.groupby(['category','type'])['weight'].sum().to_frame().reset_index()
#fig = px.bar(df, y='weight',  x='date',  color="type", barmode='group',text='weight')
#df_daily=df[df.date==str(date.today().strftime("%Y-%m-%d"))].groupby(['category'])['weight'].sum().to_frame().reset_index()
df_daily=df[df.date==df.loc[df.index[-1]]['date']].groupby(['category'])['weight'].sum().to_frame().reset_index()
print(df.loc[df.index[-1]]['date'])
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


app.layout = dbc.Container(
    [
        html.H1("Orto-Il Mio"),
        html. Hr(),
        dbc.Row([dbc.Col([
        dbc.Container ([
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Label("Category", html_for="Category"),
                                dcc.Dropdown(
                                    id="dd-category",
                                    options=[{'label':i,'value':i} for i in df_sel['Category'].unique()]
                                        ),
                            ],
                            className="mb-3",
                        ),
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Label("Type", html_for="Type"),
                                dcc.Dropdown(
                                    id="dd-type",
                                    options=[{'label':i,'value':i} for i in df_sel['Type'].unique()]
                                        ),
                            ],
                            className="mb-3",
                        )
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Label("Date  ", html_for="Date"),
                                html.Br(),
                                dcc.DatePickerSingle(
                                    id="dt-picker-date",
                                    min_date_allowed=date(2000, 1, 1),
                                    max_date_allowed=date(2025, 1, 1),
                                    initial_visible_month=date(2023, 6, 1),
                                    date=date.today(),#date(2023, 6, 1),
                                ),
                                print(type(date(2023, 6, 1)))
                                # #html.Br(),
                                # html.P(id="output"),
                            ] ,className='mb-3'
                        )
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Label("Pieces", html_for="Pieces"),
                                dbc.Input(
                                    id="in-pieces", placeholder="pieces", type="number"
                                ),
                            ],className='mb-3'
                        )
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Label("Weight", html_for="Weigth"),
                                dbc.Input(
                                    id="in-weight", placeholder="weight", type="number"
                                ),
                                #html.Br(),
                                # html.P(id="output"),
                            ] ,className='mb-3'
                        )
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Button(
                                    "Submit", id="submit", className="me-2", n_clicks=0
                                ),
                            ],className='mb-3'
                        )
                    ]
                ),
            ]
        ),
        dbc.Row([dbc.Col([html.Div([html.P("Your Entry Summary", id="output")],className='mb-3 border'
                                   )])]),
        dbc.Row([dbc.Col([html.Hr()])]),
        dbc.Row([dbc.Col([html.Div(
                            [
                                dbc.Button(
                                    "Get Data Summary", id="retrieve", className="me-2", n_clicks=0
                                ),

                            ],className='mb-3'
                        )])]),
        dbc.Row(dbc.Col([
            dbc.Container([html.P("Last harvest summary"),dash_table.DataTable(#data=df[['category','type','date','pieces','weight']].to_dict('records')
                        data=df_daily.to_dict('records')
                         , id='tbl_daily'),])
        ])),
        dbc.Row([dbc.Col([html.Hr()])]),
               
        
                        dbc.Row([dbc.Col([dbc.Container(
                            [html.P("Overall summary by Category and Type"),
                               
    #dcc.Graph(figure=fig),
    dash_table.DataTable(#data=df[['category','type','date','pieces','weight']].to_dict('records')
                        data=df_sum.to_dict('records')
                         , id='tbl'),
                         
                           
                            ],className='mb-3'
                        )])]),
   
        ], className='mb-3'),]),
        dbc.Col([]),]),

        html.Hr(),
        
    ],style={'border':'10px'}, 
)
@app.callback(
    Output('tbl','data'), 
    [Input("retrieve", "n_clicks")],
    prevent_initial_call=True,
        
)
def update_table(n):
    df = pd.DataFrame(list(collection.find()))
    print(df)
    df['_id'] = df['_id'].astype(str) 
    df_sum=df.groupby(['category','type'])['weight'].sum().to_frame().reset_index()
    #return df[['category','type','date','pieces','weight']].to_dict("records")
    return df_sum.to_dict("records")
            
@app.callback(
    Output('tbl_daily','data'), 
    [Input("retrieve", "n_clicks")],
    prevent_initial_call=True,
        
)
def update_table(n):
    df = pd.DataFrame(list(collection.find()))
    print(df)
    df['_id'] = df['_id'].astype(str) 
    df_daily=df[df.date==df.loc[df.index[-1]]['date']].groupby(['category'])['weight'].sum().to_frame().reset_index()
    #return df[['category','type','date','pieces','weight']].to_dict("records")
    return df_daily.to_dict("records")
    

@app.callback(
    Output("output", "children"),
    [Input("submit", "n_clicks")],
    [
        State("dd-category", "value"),
        State("dd-type", "value"),
        State("in-weight", "value"),
        State("in-pieces", "value"),
        State("dt-picker-date", "date"),
    ],
    prevent_initial_call=True,
)
def insertNewRecord(n, opt, type, weight, n_pieces, date):
    strOut = f"Category: {opt}, Type: {type}, Weight: {weight}, n_pieces: {n_pieces}, Date: {date}"
    record = {
        "category": opt,
        "type": type,
        "weight": weight,
        "date": date,
        "pieces": n_pieces,
    }

    collection.insert_one(record)

    return strOut


if __name__ == "__main__":
    app.run_server(debug=True)
