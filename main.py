from dash import html, dash, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
import scipy.stats
import pandas as pd

#------------------------------------------------------------------------------------------------------
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


row_input_valid_move = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Input(id="valid_move_previous_turn_number", 
                                placeholder="Previous turn number of dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1)),
                dbc.Col(dbc.Input(id="valid_move_previous_turn_face", 
                                placeholder="Previous turn face of dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                ))
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Input(id="valid_move_number", 
                    placeholder="Number of dice", 
                    type="number",
                    min=1)),
                dbc.Col(dbc.Input(id="valid_move_face", 
                            placeholder="Face of dice", 
                            type="number",
                            min=1, max=6, step=1),
                           )
            ]
        ),

    ]
)

checklist_valid_move = html.Div(
    [
        dbc.Switch(
            id="first_turn_toggle",
            label="Is this the first turn?",
            value=False,
        ),   
        # dbc.Checklist(
        #     options=[
        #         {"label": "Is this the first turn?", "value": 1}
        #     ],
        #     value=[0],
        #     id="first_turn_toggle",
        #     switch=True
        # ),
    ]
)


container_valid_mov = html.Div(
    dbc.Container(
    [
        html.H2("Is your next move a valid move ?", className="mb-0"),
        html.Br(),
        html.H4("Insert the previous turn and your current intention of play:", className="mb-0"),
        html.Br(),
        checklist_valid_move,
        html.Br(),
        row_input_valid_move,
        html.P(id = 'valid_move_response')
    ],
    fluid = True,
    className = 'py-3'
    ),
    className="p-3 bg-light rounded-3"
    )

row_input_probablilty_sin_info = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Input(id="probablilty_sin_info_number", 
                                placeholder="Current turn number of dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1)),
                dbc.Col(dbc.Input(id="probablilty_sin_info_face", 
                                placeholder="Previous turn face of dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
                dbc.Col(dbc.Input(id="probablilty_sin_info_total_dice", 
                                placeholder="Total dice in game", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1,step=1
                                ))
            ]
        ),
    ]
)



container_probability_sin_info = html.Div(
    dbc.Container(
    [
        html.H2("What is the probability of an opponents move?", className="mb-0"),
        html.Br(),
        html.H4("Insert the move, input the face of the dice, the cuantity, and the number of dice in play",
                className="mb-0"),
        html.Br(),
        row_input_probablilty_sin_info,
        html.P(id = 'probability_sin_info_response')
    ],
    fluid = True,
    className = 'py-3'
    ),
    className="p-3 bg-light rounded-3"
    )
#------------------------------------------------------------------------------------------------------
# #callbacks
@app.callback(
    [Output('valid_move_response','children')],
    [Input('first_turn_toggle','value'),
    Input('valid_move_previous_turn_face','value'),
    Input('valid_move_previous_turn_number','value'),
    Input('valid_move_face','value'),
    Input('valid_move_number','value')],

)
def valid_move(toggle, prev_move_face,prev_move_number,current_move_face,current_move_number):
    # print(toggle,prev_move_number, prev_move_face,current_move_face,current_move_number)
    if toggle:
        if None in [current_move_face,current_move_number]:
            return ['Insert value']
        else:
            return ['This is a valid move']
    else:
        if None in [prev_move_number, prev_move_face,current_move_face,current_move_number]:
            return ['Insert values']
        else:
            new_response = mayor_en_juego((current_move_number,current_move_face),
                                        (prev_move_number,prev_move_face,))
            # print(new_response)
            if new_response:
                return ['Valid move']
            else:
                return ['Unvalid move']


@app.callback(
    [Output('valid_move_previous_turn_face','style'),
    Output('valid_move_previous_turn_number','style')],
    [Input('first_turn_toggle','value')],
    prevent_initial_call= True
)
def show_previous_move(value):
    if value == True:
        return [{'display':'none'},{'display':'none'}]
    else:
        return [{'display':'block'},{'display':'block'}]

@app.callback(
    [Output('probability_sin_info_response','children')],
    [Input('probablilty_sin_info_number','value'),
    Input('probablilty_sin_info_face','value'),
    Input('probablilty_sin_info_total_dice','value')]
)
def response_probality_sin_info(number,face,total_dice):
    if None in [number,face,total_dice]:
        return  ['Insert values']
    else:
        response_new = probability_of_sin_informacion(number,face,total_dice)
        return ['The probablility is '+str(response_new)]
#------------------------------------------------------------------------------------------------------
#layout
app.layout = html.Div(children=[
    html.Center(children = [
        html.H1(children='''Liar's Dice Optimal Play''',
                className="display-3",
                style = {
                        'color' :colors['text'] 
                        }
                )]),
        container_valid_mov
            ,
        html.Br(),
        container_probability_sin_info,
    html.Div(children='''
        Dash: A web application framework for your data.
    ''')])

if __name__ == '__main__':
    app.run_server(debug=True)