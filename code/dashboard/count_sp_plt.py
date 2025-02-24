import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_fig1(df_m, df_H, df_QN, df_mouse, df_human):
    fig = make_subplots(
        rows=1, cols=2,  
        subplot_titles=['Number of cells with channel recording',
                        'Number of cells with channel recording and ttypes'],
        shared_yaxes=False,
        horizontal_spacing=0.2)
    
    fig.add_trace(go.Bar(
        x=['Mouse', 'Human', 'NHP'],
        y=[df_m.shape[0], df_H.shape[0], df_QN.shape[0]],
        marker_color=['teal', 'salmon', 'cornflowerblue'],
        opacity=0.6
    ), row=1, col=1)
    

    fig.add_trace(go.Bar(
        x=['Mouse', 'Human'],
        y=[df_mouse.shape[0], df_human.shape[0]],
        marker_color=['teal', 'salmon', 'cornflowerblue'],
        opacity=0.6,
    ), row=1, col=2)

    # Layout
    fig.update_layout(
        width=1000,  
        height=400, 
        showlegend=False,
        xaxis_title="Species",
        xaxis2_title="Species",
        yaxis_title="Number of cells",
        yaxis2_title="Number of cells",
        title=dict(text="Cells with channel recording by species",
            x=0.5,
            xanchor='center',
            font=dict(
                family='Arial',
                size=20,
                color='black',
                weight='bold'))
    )

    return fig
