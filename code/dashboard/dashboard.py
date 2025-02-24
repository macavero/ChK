import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import os
import dash_html_components as html


# Import the functions to create the figures
from count_sp_plt import create_fig1
from count_subclasses_plt import create_fig3


# Load the data
cwd = os.getcwd()
densities_path = "../../data/channel_data_densities.xlsx"
df_densities = pd.read_excel(densities_path, sheet_name='peak_current_densities')

# Human (sorting with Regex)
pattern_H = r'^H[0-9]\d'
df_pattern_H = df_densities.copy()
df_reg_H = df_pattern_H[df_pattern_H['cell'].str.contains(pattern_H, regex=True)]
df_H = df_reg_H.reset_index(drop=True)

# NHP (sorting with Regex)
pattern_QN = r'^QN[0-9]\d'
df_pattern_QN = df_densities.copy()
df_reg_QN = df_pattern_QN[df_pattern_QN['cell'].str.contains(pattern_QN, regex=True)]
df_QN = df_reg_QN.reset_index(drop=True)

# Mouse
pattern_m = r'^(H[0-9]\d|QN[0-9]\d)'
df_m = df_densities[~df_densities['cell'].str.contains(pattern_m, regex=True)].reset_index(drop=True)

# Human - Use tree_subclass and tree_cluster for ttype
h_ttypes_path = '//allen/programs/celltypes/workgroups/rnaseqanalysis/shiny/patch_seq/star/human/human_patchseq_MTG_current/mapping.df.lastmap.csv'
df_human_ttypes = pd.read_csv(h_ttypes_path) 
df_human_ttypes_reduced = df_human_ttypes[['cell_name_label', 'tree_subclass', 'tree_cluster', 'tree_class']]

df_human_ch_tt = pd.merge(left = df_H, left_on = 'cell',
            right = df_human_ttypes_reduced, right_on = 'cell_name_label', how = 'inner')

# Human - merge ephys
df_hum_ephys = pd.read_csv('../../data/results_human_query.csv')
df_human = pd.merge(left = df_human_ch_tt, left_on = 'cell',
            right = df_hum_ephys, right_on = 'name', how = 'inner')

# Mouse 
m_ttypes_path = '//allen/programs/celltypes/workgroups/rnaseqanalysis/shiny/patch_seq/star/mouse/mouse_patchseq_WB_current/mapping.df.lastmap.csv'
df_mouse_ttypes = pd.read_csv(m_ttypes_path)
df_mouse_ch_tt = pd.merge(left = df_m, left_on = 'cell',
                    right = df_mouse_ttypes, right_on='cell_name', how='inner')

# Merge with ephys data (query from LIMS)
df_mouse_ephys = pd.read_csv('../../data/results_mouse_query.csv')
df_mouse = pd.merge(left = df_mouse_ch_tt, left_on = 'cell',
            right = df_mouse_ephys, right_on = 'name', how = 'inner')

# New column for class
df_mouse['class'] = df_mouse['best.class_label'].apply(
    lambda x: 'Glutamatergic' if 'Glut' in x else ('GABAergic' if 'GABA' in x else 'Unknown'))

# Create the figures
fig1 = create_fig1(df_m, df_H, df_QN,df_mouse, df_human)
# fig2 = create_fig2(df_mouse, df_human)
classification_m = 'subclass'
classification_h = 'tree_subclass'
fig3 = create_fig3(df_mouse, df_human, classification_m, classification_h)

# Initialize the Dash app
app = dash.Dash(__name__,
                external_stylesheets=["https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap"])
app.title = "Cell Recordings by species"

# Define the layout of the app
app.layout = html.Div(
    id="app-container",
    children=[
        html.H1("Cells Recordings by Species"),
        html.P("Count recordings and ttypes"),
        # Contenedor de gráficos principales
        html.Div(
            children=[
                dcc.Graph(figure=fig1, style={'width': '100%', 'max-width': '900px', 'height': '400px', 'margin': '0 auto'}),
                dcc.Graph(figure=fig3, style={'width': '100%', 'max-width': '900px', 'height': '400px', 'margin': '0 auto'})
            ],
            style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center',
                   'justify-content': 'center', 'margin-bottom': '200px'}
        ),
        # Contenedor para dropdowns y scatter plot
                # Dropdowns y gráficos para el Mouse
        html.Div(
            children=[
                html.H3("Mouse Dataset", style={'margin-bottom': '10px'}),
                dcc.Dropdown(
                    id='xaxis-selector-mouse',
                    options=[{'label': col, 'value': col} for col in df_mouse.columns],
                    value=df_mouse.columns[1],
                    placeholder='Select x-axis variable',
                    style={'width': '40%', 'margin': '0 auto', 'margin-bottom': '15px'}
                ),
                dcc.Dropdown(
                    id='yaxis-selector-mouse',
                    options=[{'label': col, 'value': col} for col in df_mouse.columns],
                    value=df_mouse.columns[2],
                    placeholder='Select y-axis variable',
                    style={'width': '40%', 'margin': '0 auto'}
                ),
                dcc.Dropdown(
                    id='color-selector-mouse',  # Nuevo dropdown para seleccionar el color
                    options=[
                        {'label': 'Type', 'value': 'ttype'}, #'ttype', 'supertype', 'subclass'
                        {'label': 'Supertype', 'value': 'supertype'},
                        {'label': 'Subclass', 'value': 'subclass'},
                        {'label': 'Class', 'value': 'class'},
                    ],
                    value='subclass',  # Valor por defecto
                    placeholder='Select color variable',
                    style={'width': '40%', 'margin': '0 auto', 'margin-top': '15px'}
                ),
                dcc.Checklist(
                    id='category-checklist-mouse',
                    options=[],  # Se llenará dinámicamente
                    value=[],  # Vacío por defecto
                    inline=True
                ),
                dcc.Graph(id='scatter-plot-mouse', style={'width': '50%', 'height': '500px', 'margin': '0 auto'})
            ],
            style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center',
                   'justify-content': 'center'}
        ),
        
        # Dropdowns y gráficos para el Human
        html.Div(
            children=[
                html.H3("Human Dataset"),
                dcc.Dropdown(
                    id='xaxis-selector-human',
                    options=[{'label': col, 'value': col} for col in df_human.columns],
                    value=df_human.columns[1],
                    placeholder='Select x-axis variable',
                    style={'width': '40%', 'margin': '0 auto'}
                ),
                dcc.Dropdown(
                    id='yaxis-selector-human',
                    options=[{'label': col, 'value': col} for col in df_human.columns],
                    value=df_human.columns[2],
                    placeholder='Select y-axis variable',
                    style={'width': '40%', 'margin': '0 auto'}
                ),
                dcc.Dropdown(
                    id='color-selector-human',  # Nuevo dropdown para seleccionar el color
                    options=[
                        {'label': 'Subclass', 'value': 'tree_subclass'}, #'ttype', 'supertype', 'subclass'
                        {'label': 'Class', 'value': 'tree_class'},
                        {'label': 'Cluster', 'value': 'tree_cluster'}
                    ],
                    value='tree_subclass',  # Valor por defecto
                    placeholder='Select color variable',
                    style={'width': '40%', 'margin': '0 auto', 'margin-top': '15px'}
                ),
                    
                dcc.Checklist(
                    id='category-checklist',
                    options=[],  # Se llenará dinámicamente
                    value=[],  # Vacío por defecto
                    inline=True
                ),
                dcc.Graph(id='scatter-plot-human', style={'width': '50%', 'height': '500px', 'margin': '0 auto'})
            ],
            style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center',
                'justify-content': 'center'}
            
        )
    ]
)


#                                           Mouse                                           #

# Callback para actualizar las opciones del checklist basado en la columna de color seleccionada en Mouse
@app.callback(
    [Output('category-checklist-mouse', 'options'),
     Output('category-checklist-mouse', 'value')],
    [Input('color-selector-mouse', 'value'),
     Input('category-checklist-mouse', 'value')]
)
def update_checklist_and_selection_mouse(color_col, selected_values):
    if not color_col or color_col not in df_mouse.columns:
        return [], []

    # Obtener categorías únicas
    unique_categories = df_mouse[color_col].dropna().unique().tolist()
    options = [{'label': 'All', 'value': 'All'}] + [{'label': cat, 'value': cat} for cat in unique_categories]

    # Si "All" está en la selección, marcar todas las opciones
    if "All" in selected_values:
        return options, ["All"] + unique_categories  

    # Si "All" NO está pero antes estaba, significa que fue deseleccionado
    if not set(selected_values).intersection(set(unique_categories)):  
        return options, []  # Vaciar la selección completamente

    return options, selected_values  # Mantener la selección manual


# Modificación del callback para el scatter plot de Mouse
@app.callback(
    Output('scatter-plot-mouse', 'figure'),
    [Input('xaxis-selector-mouse', 'value'),
     Input('yaxis-selector-mouse', 'value'),
     Input('color-selector-mouse', 'value'),
     Input('category-checklist-mouse', 'value')]
)
def update_scatter_mouse(x_col, y_col, color_col, selected_categories):
    if not x_col or not y_col or color_col not in df_mouse.columns:
        return px.scatter(title="Invalid column selection.")
    
    filtered_df = df_mouse[[x_col, y_col, 'ttype', 'class', 'supertype', 'subclass']].dropna()
    
    if filtered_df.empty:
        return px.scatter(title="No data available for selected columns.")
    
    # Manejo de "All": si está seleccionado, mostrar todo sin grises
    if "All" in selected_categories or not selected_categories:
        selected_categories = df_mouse[color_col].dropna().unique().tolist()
    
    # Aplicar colores: gris para los no seleccionados
    filtered_df['highlight'] = filtered_df[color_col].apply(lambda x: x if x in selected_categories else 'Other')

    # Crear scatter plot
    fig = px.scatter(
        filtered_df, 
        x=x_col, 
        y=y_col, 
        color='highlight',
        color_discrete_map={'Other': 'gray'}
    )

    fig.update_layout(title=dict(text="Mouse Scatter Plot", x=0.5, font=dict(size=18)))
    return fig



#                                             Human                                           #

# Callback para actualizar las opciones del checklist basado en la columna de color seleccionada

@app.callback(
    [Output('category-checklist', 'options'),
     Output('category-checklist', 'value')],
    [Input('color-selector-human', 'value'),
     Input('category-checklist', 'value')]
)
def update_checklist_and_selection(color_col, selected_values):
    if not color_col or color_col not in df_human.columns:
        return [], []

    # Obtener categorías únicas
    unique_categories = df_human[color_col].dropna().unique().tolist()
    options = [{'label': 'All', 'value': 'All'}] + [{'label': cat, 'value': cat} for cat in unique_categories]

    # Si "All" está en la selección, marcar todas las opciones
    if "All" in selected_values:
        return options, ["All"] + unique_categories  

    # Si "All" NO está pero antes estaba, significa que fue deseleccionado
    if not set(selected_values).intersection(set(unique_categories)):  
        return options, []  # Vaciar la selección completamente

    return options, selected_values  # Mantener la selección manual"


# Modificación del callback para el scatter plot de Human
@app.callback(
    Output('scatter-plot-human', 'figure'),
    [Input('xaxis-selector-human', 'value'),
     Input('yaxis-selector-human', 'value'),
     Input('color-selector-human', 'value'),
     Input('category-checklist', 'value')]
)
def update_scatter_human(x_col, y_col, color_col, selected_categories):
    if not x_col or not y_col or color_col not in df_human.columns:
        return px.scatter(title="Invalid column selection.")
    
    filtered_df = df_human[[x_col, y_col, 'tree_subclass', 'tree_class', 'tree_cluster']].dropna()
    
    if filtered_df.empty:
        return px.scatter(title="No data available for selected columns.")
    
    # Manejo de "All": si está seleccionado, mostrar todo sin grises
    if "All" in selected_categories or not selected_categories:
        selected_categories = df_human[color_col].dropna().unique().tolist()
    
    # Aplicar colores: gris para los no seleccionados
    filtered_df['highlight'] = filtered_df[color_col].apply(lambda x: x if x in selected_categories else 'Other')

    # Crear scatter plot
    fig = px.scatter(
        filtered_df, 
        x=x_col, 
        y=y_col, 
        color='highlight',
        color_discrete_map={'Other': 'gray'}
    )

    fig.update_layout(title=dict(text="Human Scatter Plot", x=0.5, font=dict(size=18)))
    return fig

# Execute the app
if __name__ == "__main__":
    app.run_server(debug=True)
