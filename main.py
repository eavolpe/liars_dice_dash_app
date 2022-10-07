from dash import Dash, html, dcc, dash
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
import scipy.stats
import pandas as pd

#-------------------------------------------------------------------------------------------------------
# dash initialization

app = dash.Dash(external_stylesheets=[dbc.themes.LITERA])
app.title = 'Optimal play '
colors = {
    'text' :'#05445E'
}
#------------------------------------------------------------------------------------------------------
#backend
def probability_of_sin_informacion(x,y,dados_restantes):
    if y == 1:
        prob =(1-scipy.stats.binom.cdf(x, dados_restantes, 1/6))+scipy.stats.binom.pmf(x,dados_restantes,1/6)
        return prob
    else:
        prob = (1-scipy.stats.binom.cdf(x, dados_restantes, 1/3))+scipy.stats.binom.pmf(x,dados_restantes,1/3)
        return prob

def probability_of_informacion(x,y,dados_totales,mis_dados):
    if y == 1:
        k = mis_dados.count(1)
        if k == x:
            return 1
        else:
            return probability_of_sin_informacion(x-k,1,dados_totales-len(mis_dados))
        
    else:
        unos = mis_dados.count(1)
        k = mis_dados.count(y)
        if k+unos == x:
            return 1
        else:
            return probability_of_sin_informacion(x-k-unos,y,dados_totales-len(mis_dados))

def mayor_en_juego(a,b):
    if a[1] == 1:
        if b[1] == 1:
            if a[0] > b[0]:
                return True
            else:
                return False
        else:
            if 2*a[0] > b[0]:
                return True
            else:
                return False
    else:
        if b[1]==1:
            if 2*b[0] < a[0]:
                return True
            else:
                return False
        else:
            if a[0] > b[0]:
                return True
            if a[0] == b[0]:
                if a[1] > b[1]:
                    return True
                else:
                    return False
            if a[0] < b[0]:
                return False
             
#------------------------------------------------------------------------------------------------------
#front end
#jumbotron


checklist_valid_move = html.Div(
    [
        
        dbc.Checklist(
            options=[
                {"label": "Is this the first turn?", "value": 1}
            ],
            value=[1],
            id="switches-input",
            switch=True
        ),
    ]
)


toast_valid_move = dbc.Toast(
    [
        html.P("Insert the previous turn and your current intention of play:", className="mb-0"),
        checklist_valid_move
    ],
    header="Valid move",
    )
#dbc.Label("Choose a bunch"),




app.layout = html.Div(children=[
    html.Center(children = [
        html.H1(children='''Liar's Dice Optimal Play''',
        style = {
            'color' :colors['text'] 
        }
        )
    ]),
    toast_valid_move,
    html.Div(children='''
        Dash: A web application framework for your data.
    '''),
])

if __name__ == '__main__':
    app.run_server(debug=True)