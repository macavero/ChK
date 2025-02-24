import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_fig3(df_mouse, df_human, classification_m, classification_h):
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=["Mouse", "Human"], 
        shared_yaxes=False,
        column_widths=[0.8, 0.2],
        horizontal_spacing=0.2 
    )

    # Add first subplot with Mouse data
    fig.add_trace(
        go.Bar(
            y=df_mouse[classification_m].value_counts().index,
            x=df_mouse[classification_m].value_counts(),
            orientation='h',
            marker=dict(color='teal', opacity=0.6),
            name='Mouse'
        ),
        row=1, col=1  # position of the graph in the subplot
    )

    # Second subplot with Human data
    fig.add_trace(
        go.Bar(
            y=df_human[classification_h].value_counts().index,
            x=df_human[classification_h].value_counts(),
            orientation='h',
            marker=dict(color='salmon', opacity=0.6),
            name='Human'
        ),
        row=1, col=2 # position of the graph in the subplot
    )

    # Update layout
    fig.update_layout(
        barmode='stack', 
        width=1050,  # Adjust the total width
        height=600,  
        title=dict(text="Cells with Channel Recording by subclass",
                   x=0.5,
                   xanchor='center',
                   font=dict(
                       family='Arial',
                       size=20,
                       color='black',
                       weight='bold')),
        showlegend=False,
        xaxis_title="Number of cells",
        xaxis2_title="Number of cells",
        yaxis_title=f"{classification_m}",
        yaxis2_title=f"{classification_h}"
    )

    return fig

