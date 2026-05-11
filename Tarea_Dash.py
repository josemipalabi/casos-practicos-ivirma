import dash
from dash import dcc
from dash import html
import pandas as pd
import plotly.graph_objs as go
import plotly.colors as pc
from sklearn.manifold import TSNE
from dash.dependencies import Input, Output
from dash import dash_table
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Preprocesado de los datos
df_raw = pd.read_csv("Arritmias.csv")
float_cols = df_raw.columns[1:-4]
df = df_raw.copy()
for i in range(len(float_cols)):
      df[float_cols[i]] = df[float_cols[i]].str.replace(",", ".").astype(float)

# Realizar t-SNE
X = df.drop(columns = ['PACIENTES', 'EDAD', 'SEXO', 'AV'], axis=1)
tsne = TSNE(n_components=2, random_state=42)
tsne_results = tsne.fit_transform(X)
df_tsne = pd.DataFrame(tsne_results, columns=['TSNE1', 'TSNE2'])
df_tsne['PACIENTES'] = df['PACIENTES']
df_tsne['EDAD'] = df['EDAD']
df_tsne['SEXO'] = df['SEXO']
df_tsne['AV'] = df['AV']

# Calculamos histogramas
variables_hist = ['LV MASS (g)', 'CHANNEL MASS (g)', 'BZ + CORE (g)', 'BZ + CORE (%)', 'BZ (g)', 'BZ (%)', 'CORE (g)', 'CORE (%)', 'LVEF']
x_labels = ['Masa (g)', 'Masa (g)', 'Masa (g)', 'Porcentaje (%)', 'Masa (g)', 'Porcentaje (%)', 'Masa (g)', 'Porcentaje (%)', 'Fuerza de ejección']

# Lista de gráficos de histogramas
histograms = []
for i, var in enumerate(variables_hist):
    hist = dcc.Graph(
        figure=go.Figure(
            data=[go.Histogram(x=df[var], nbinsx=30, marker_color='lightslategray')],
            layout=go.Layout(
                title=f'Histograma de {var}',
                xaxis_title=x_labels[i],
                yaxis_title='Frecuencia',
                bargap=0.1,
                height=300,
                margin={'l': 40, 'r': 40, 't': 40, 'b': 40}
            )
        ),
        style={'width': '45%', 'display': 'inline-block', 'margin': '20px'}
    )
    histograms.append(hist)

app.layout = html.Div([
    html.H1('Tarea 2 VAD: Visualización Web del Análisis de Marcadores mediante Dash'),
    html.Div('Autor: José Miguel Palazón Caballero', style={'fontStyle': 'italic', 'fontSize': '30px'}),
    html.Br(),

    html.P('Seleccione la variable por la cual colorear los puntos en el gráfico:', style={'fontSize': '18px'}),
    dcc.Dropdown(
        id='color-selector',
        options=[
            {'label': 'Sexo', 'value': 'SEXO'},
            {'label': 'Edad', 'value': 'EDAD'},
            {'label': 'AV (Arritmia)', 'value': 'AV'}
        ],
        value='AV',
        style={'width': '50%'}
    ),
    
    dcc.Graph(id='tsne-plot', hoverData={}),

    html.Br(),
    html.H4("Detalles del paciente seleccionado:"),
    dash_table.DataTable(
        id='data-table',
        columns=[
            {'name': col, 'id': col} for col in df.columns
        ],
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={'fontWeight': 'bold'},
        style_data_conditional=[]
    ),

    html.H2("Distribución de Marcadores en la Población"),
    dcc.Store(id='hovered-patient'),
    html.Div(id='histograms-container', style={'textAlign': 'center'})
    ])

@app.callback(
    [Output('tsne-plot', 'figure'),
    Output('data-table', 'style_data_conditional')],
    Input('color-selector', 'value')
)
def update_graph(selected_var):
    if selected_var == 'AV':
        data = [
            go.Scatter(
                x=df_tsne[df_tsne['AV'] == 0]['TSNE1'],
                y=df_tsne[df_tsne['AV'] == 0]['TSNE2'],
                mode='markers',
                text=df_tsne[df_tsne['AV'] == 0]['PACIENTES'] + '<br>AV = 0',
                hoverinfo='text',
                marker={'size': 12, 'color': 'lightblue'},
                name='No Arritmia'
            ),
            go.Scatter(
                x=df_tsne[df_tsne['AV'] == 1]['TSNE1'],
                y=df_tsne[df_tsne['AV'] == 1]['TSNE2'],
                mode='markers',
                text=df_tsne[df_tsne['AV'] == 1]['PACIENTES'] + '<br>AV = 1',
                hoverinfo='text',
                marker={'size': 12, 'color': 'darkorange'},
                name='Arritmia'
            )
        ]

        style_data_conditional = [
            {
                'if': {'column_id': 'AV', 'filter_query': '{AV} = 0'},
                'backgroundColor': 'lightblue',
                'color': 'black'
            },
            {
                'if': {'column_id': 'AV', 'filter_query': '{AV} = 1'},
                'backgroundColor': 'darkorange',
                'color': 'white'
            }
        ]

    elif selected_var == 'SEXO':
        data = [
            go.Scatter(
                x=df_tsne[df_tsne['SEXO'] == 1]['TSNE1'],
                y=df_tsne[df_tsne['SEXO'] == 1]['TSNE2'],
                mode='markers',
                text=df_tsne[df_tsne['SEXO'] == 1]['PACIENTES'] + '<br>Sexo = Hombre',
                hoverinfo='text',
                marker={'size': 12, 'color': 'lightblue'},
                name='Hombre'
            ),
            go.Scatter(
                x=df_tsne[df_tsne['SEXO'] == 2]['TSNE1'],
                y=df_tsne[df_tsne['SEXO'] == 2]['TSNE2'],
                mode='markers',
                text=df_tsne[df_tsne['SEXO'] == 2]['PACIENTES'] + '<br>Sexo = Mujer',
                hoverinfo='text',
                marker={'size': 12, 'color': 'darkorange'},
                name='Mujer'
            )
        ]

        style_data_conditional = [
            {
                'if': {'column_id': 'SEXO', 'filter_query': '{SEXO} = 1'},
                'backgroundColor': 'lightblue',
                'color': 'black'
            },
            {
                'if': {'column_id': 'SEXO', 'filter_query': '{SEXO} = 2'},
                'backgroundColor': 'darkorange',
                'color': 'white'
            }
        ]

    elif selected_var == 'EDAD':
        data = [
            go.Scatter(
                x=df_tsne['TSNE1'],
                y=df_tsne['TSNE2'],
                mode='markers',
                text=df_tsne['PACIENTES'] + '<br>Edad = ' + df['EDAD'].astype(str),
                hoverinfo='text',
                marker={
                    'size': 12,
                    'color': df_tsne['EDAD'],
                    'colorscale': 'sunsetdark',
                    'colorbar': {'title': 'EDAD'}
                },
                name='EDAD'
            )
        ]

        style_data_conditional = [
            {
                'if': {'column_id': 'EDAD'},
                'backgroundColor': 'purple',
                'color': 'white'
            }
        ]
    
    layout = go.Layout(
        title='Proyección en 2D de la población de pacientes mediante t-SNE',
        titlefont={'size': 20, 'family': 'Arial', 'color': 'black'},
        xaxis={'title': 'Dimensión 1'},
        yaxis={'title': 'Dimensión 2'},
        margin={'l': 40, 'b': 40, 't': 30, 'r': 10},
        hovermode='closest',
        legend={'title': {'text': f'{selected_var}', 'font': {'size': 16,  'color': 'black',  'family': 'Arial'}}, 'x': 0.8, 'y': 1}
    )
    
    return {'data': data, 'layout': layout}, style_data_conditional


@app.callback(
    [Output('data-table', 'data'),
    Output('hovered-patient', 'data')],
    Input('tsne-plot', 'hoverData')
)
def display_hover_data(hoverData):
    if hoverData is None or 'points' not in hoverData or len(hoverData['points']) == 0:
        return [], None  # ¡Ahora devuelves dos cosas!


    paciente_hovered = hoverData['points'][0]['text'].split('<br>')[0]

    patient_data = df[df['PACIENTES'] == paciente_hovered].iloc[0]
    patient_info = {col: patient_data[col] for col in df.columns}

    return [patient_info], patient_info

@app.callback(
    Output('histograms-container', 'children'),
    Input('hovered-patient', 'data')
)
def update_histograms(patient_info):
    histograms = []

    predefined_colors = [
    "#00FF00", "#33FF00", "#66FF00", "#99FF00", "#CCFF00",
    "#FFFF00", "#FFEE00", "#FFDD00", "#FFCC00", "#FFBB00",
    "#FFAA00", "#FF9900", "#FF8800", "#FF7700", "#FF6600",
    "#FF5500", "#FF4400", "#FF3300", "#FF2200", "#FF1100",
    "#FF0000", "#EE0000", "#DD0000", "#CC0000", "#BB0000",
    "#AA0000", "#990000", "#880000", "#770000", "#660000"
    ]

    for i, var in enumerate(variables_hist):
        counts, bin_edges = np.histogram(df[var], bins=30)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        colors = ['lightslategray'] * len(counts)

        if patient_info is not None:
            patient_value = float(patient_info[var])

            for j in range(len(bin_edges) - 1):
                if bin_edges[j] <= patient_value < bin_edges[j + 1]:
                    colors[j] = predefined_colors[j]
                    break
            else:
                # Si cae exactamente en el último borde
                if patient_value == bin_edges[-1]:
                    colors[-1] = predefined_colors[-1]

        fig = go.Figure(go.Bar(
            x=bin_centers,
            y=counts,
            marker_color=colors,
            width=[(bin_edges[1] - bin_edges[0]) * 0.9] * len(counts)
        ))

        fig.update_layout(
            title=f'Histograma de {var}',
            xaxis_title=x_labels[i],
            yaxis_title='Frecuencia',
            bargap=0.1,
            height=300,
            margin={'l': 40, 'r': 40, 't': 40, 'b': 40},
            showlegend=False
        )

        hist = dcc.Graph(figure=fig, style={'width': '45%', 'display': 'inline-block', 'margin': '20px'})
        histograms.append(hist)

    return histograms

if __name__ == '__main__':
    app.run(debug=True)