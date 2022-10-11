from sqlite3 import enable_shared_cache
from dash import html, dash, Input, Output, dash_table
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

def mis_opciones_en_turno(lista_mis_dados,dados_totales,turno_anterior = None):
    dict_opciones = {}
    if turno_anterior == None:
        for i in range(dados_totales):
            for j in range(6):
                dict_opciones['('+str(i+1)+','+str(j+1)+')'] = probability_of_informacion(i+1,j+1,dados_totales,lista_mis_dados)
    else:
        for i in range(dados_totales):
            for j in range(6):
                if mayor_en_juego((i+1,j+1),turno_anterior):
                    dict_opciones['('+str(i+1)+','+str(j+1)+')'] = probability_of_informacion(i+1,j+1,dados_totales,lista_mis_dados)
    dict_opciones['Dudo que allan '+'('+str(turno_anterior[0])+','+str(turno_anterior[1])+')'] = 1-probability_of_informacion(turno_anterior[0],turno_anterior[1],dados_totales,lista_mis_dados)
    #casarse
    if turno_anterior[1]== 1:
        k =lista_mis_dados.count(1)
        dict_opciones['Me caso con '+'('+str(turno_anterior[0])+','+str(turno_anterior[1])+')'] = scipy.stats.binom.pmf(turno_anterior[0]-k,dados_totales-len(lista_mis_dados),1/6)
    else:
        unos = lista_mis_dados.count(1)
        k =lista_mis_dados.count(turno_anterior[1])
        dict_opciones['Me caso con '+'('+str(turno_anterior[0])+','+str(turno_anterior[1])+')'] = scipy.stats.binom.pmf(turno_anterior[0]-k-unos,dados_totales-len(lista_mis_dados),1/3)
    dict_opciones = sorted(dict_opciones.items(),key=lambda x: x[1], reverse = True)
    return dict_opciones
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
                                placeholder="Previous turn number of dice", 
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


row_input_probablilty_with_info = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Input(id="probablilty_info_number", 
                                placeholder=" Number of dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1)),
                dbc.Col(dbc.Input(id="probablilty_info_face", 
                                placeholder="Face of dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
                dbc.Col(dbc.Input(id="probablilty_info_total_dice", 
                                placeholder="Total dice in game", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1,step=1
                                ))
            ]
        ),
        html.Br(),
        dbc.Row([
                dbc.Select(
                    id="select_dice_amount_info",
                    placeholder='How many dice do you currently have ?',
                    options=[
                        {"label": "1", "value": "1"},
                        {"label": "2", "value": "2"},
                        {"label": "3", "value": "3"},
                        {"label": "4", "value": "4"},
                        {"label": "5", "value": "5"},
                        {"label": "6", "value": "6"},
                    ],
                )
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(dbc.Input(id="dice_1", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
            dbc.Col(dbc.Input(id="dice_2", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
            dbc.Col(dbc.Input(id="dice_3", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
            dbc.Col(dbc.Input(id="dice_4", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
            dbc.Col(dbc.Input(id="dice_5", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
            dbc.Col(dbc.Input(id="dice_6", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                ))
        ]

        )
    ]
)

container_probability_info = html.Div(
    dbc.Container(
    [
        html.H2("What is the probability of my next move considering my current dice?", className="mb-0"),
        html.Br(),
        html.H4("How many dice do you currently have ?",
                className="mb-0"),
        html.Br(),
        row_input_probablilty_with_info,
        html.P(id = 'probability_info_response')
    ],
    fluid = True,
    className = 'py-3'
    ),
    className="p-3 bg-light rounded-3"
    )

row_input_probablilty_with_moves = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Input(id="probablilty_moves_number", 
                                placeholder=" Number of dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1)),
                dbc.Col(dbc.Input(id="probablilty_moves_face", 
                                placeholder="Face of dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
                dbc.Col(dbc.Input(id="probablilty_moves_total_dice", 
                                placeholder="Total dice in game", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1,step=1
                                ))
            ]
        ),
        html.Br(),
        dbc.Row([
                dbc.Select(
                    id="select_moves_amount_info_moves",
                    placeholder='How many dice do you currently have ?',
                    options=[
                        {"label": "1", "value": "1"},
                        {"label": "2", "value": "2"},
                        {"label": "3", "value": "3"},
                        {"label": "4", "value": "4"},
                        {"label": "5", "value": "5"},
                        {"label": "6", "value": "6"},
                    ],
                )
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(dbc.Input(id="dice_1_moves", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
            dbc.Col(dbc.Input(id="dice_2_moves", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
            dbc.Col(dbc.Input(id="dice_3_moves", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
            dbc.Col(dbc.Input(id="dice_4_moves", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
            dbc.Col(dbc.Input(id="dice_5_moves", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                )),
            dbc.Col(dbc.Input(id="dice_6_moves", 
                                placeholder="Insert dice", 
                                type="number",
                                style  = {'display': 'block'},
                                min=1, max=6, step=1
                                ))
        ]

        )
    ]
)

container_probability_with_moves_info = html.Div(
    dbc.Container(
    [
        html.H2("What are your next posible moves with probability", className="mb-0"),
        html.Br(),
        html.H4("Insert dice and previous moves?",
                className="mb-0"),
        html.Br(),
        row_input_probablilty_with_moves,
        dash_table.DataTable(
        id='table',
        data=[]),
        html.P(id = 'table_status')
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
    Input('valid_move_number','value'),]

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

@app.callback(
    [Output('dice_1','style'),
    Output('dice_2','style'),
    Output('dice_3','style'),
    Output('dice_4','style'),
    Output('dice_5','style'),
    Output('dice_6','style'),],
    [Input('select_dice_amount_info','value')]
)
def reduce_number_of_dice(value):
    if value == None:
        return [{'display':'none'}]*6
    else:
        hide = 6-int(value)
        return [{'display':'block'}]*int(value)+[{'display':'none'}]*hide

@app.callback(
    [Output('probability_info_response','children')],
    [Input('dice_1','value'),
    Input('dice_2','value'),
    Input('dice_3','value'),
    Input('dice_4','value'),
    Input('dice_5','value'),
    Input('dice_6','value'),
    Input('select_dice_amount_info','value'),
    Input('probablilty_info_number','value'),
    Input('probablilty_info_face','value'),
    Input('probablilty_info_total_dice','value')],
    prevent_initial_call= True
)
def probablity_of_informacion(dice1,dice2,dice3,dice4,dice5,dice6,status,number,face,total_dice):
    if None in [face,number,total_dice]:
        return ['Insert values']
    else:
        if status == None:
            return ['Insert values']
        else:
            int_status = int(status)
            dice = [dice1,dice2,dice3,dice4,dice5,dice6]
            if None in dice[0:int_status]:
                return ['Insert values']
            else:
                return [str(probability_of_informacion(number,face,total_dice,dice[0:int_status]))]

@app.callback(
    [Output('dice_1_moves','style'),
    Output('dice_2_moves','style'),
    Output('dice_3_moves','style'),
    Output('dice_4_moves','style'),
    Output('dice_5_moves','style'),
    Output('dice_6_moves','style'),],
    [Input('select_moves_amount_info_moves','value')]
)

def show_dice_list_container(value):
    if value == None:
        return [{'display':'none'}]*6
    else:
        hide = 6-int(value)
        return [{'display':'block'}]*int(value)+[{'display':'none'}]*hide

@app.callback(
    [
    Output('table','data'),
    Output('table_status','children'),],
    [Input('select_moves_amount_info_moves','value'),
    Input('dice_1_moves','value'),
    Input('dice_2_moves','value'),
    Input('dice_3_moves','value'),
    Input('dice_4_moves','value'),
    Input('dice_5_moves','value'),
    Input('dice_6_moves','value'),
    Input('probablilty_moves_total_dice','value'),
    Input('probablilty_moves_face','value'),
    Input('probablilty_moves_number','value')]
)
def show_moves_probability(amount_of_dice,
                        dice1,
                        dice2,
                        dice3,
                        dice4,
                        dice5,
                        dice6,
                        total_dice,
                        move_face,
                        move_number):
    if None in [total_dice,move_face,move_number]:
        return [None, 'Insert values']
    else:
        if amount_of_dice == None:
            return [None,'Insert values']
        else:
            int_status = int(amount_of_dice)
            dice = [dice1,dice2,dice3,dice4,dice5,dice6,]
            if None in dice[0:int_status]:
                return [None,'Insert values']
            else:
                resp = mis_opciones_en_turno(dice[0:int_status],total_dice,(move_number,move_face))
                resp_list = []
                for i in resp:
                    resp_list.append(({'Name':i[0],'Value':i[1]}))
                return [resp_list,None]
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
        html.Br(),
        container_probability_info,
        html.Br(),
        container_probability_with_moves_info,
        html.Div(children='''
        Dash: A web application framework for your data.
    ''')])

if __name__ == '__main__':
    app.run_server(debug=True)