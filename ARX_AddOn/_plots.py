import pandas as pd
import plotly
pd.options.plotting.backend = "plotly"
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# # Using pandas plot
# def df_plot(df):
#     if df.empty:
#         df = pd.DataFrame()
#         fig = df.plot()
#         fig.data = []
#         return None
#     fig = df.plot()
#     fig.layout.paper_bgcolor = 'rgba(0,0,0,0)'
#     fig.layout.plot_bgcolor = 'rgba(0,0,0,0)'
#     fig.layout.dragmode = "select"
#     fig.layout.modebar = {
#         'bgcolor': 'rgba(0, 0, 0, 0)',
#         'color': 'rgba(221, 221, 221, 1)',
#         'activecolor': 'rgba(0, 121, 96, 1)'
#     }
#     return fig



def df_plot(df, fig=None, plot_type='train'):
    if df.empty:
        df = pd.DataFrame()
#         fig = df.plot()
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Training Results',  'Validation Results'))
        fig.add_trace(go.Scatter(x=df.index, y=df), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df), row=1, col=2)
        fig['layout']['xaxis']['title']='Time'
        fig['layout']['xaxis2']['title']='Time'
        fig['layout']['yaxis']['title']='Value'
        fig['layout']['yaxis2']['title']='Value'
        return fig

    
    if plot_type == 'train':
#     fig = make_subplots(rows=1, cols=2, subplot_titles=('Training Results',  'Validation Results'))
#     fig.layout.paper_bgcolor = 'rgba(0,0,0,0)'
#     fig.layout.plot_bgcolor = 'rgba(0,0,0,0)'
#     fig.layout.dragmode = "select"
#     fig.layout.modebar = {
#         'bgcolor': 'rgba(0, 0, 0, 0)',
#         'color': 'rgba(221, 221, 221, 1)',
#         'activecolor': 'rgba(0, 121, 96, 1)'
#     }
        fig_data = list(fig.data)
        fig_data_c = fig_data.copy()
        for i in range(len(fig_data)):
            if fig_data[i].xaxis == 'x':
                fig_data_c.remove(fig_data[i])

        fig.data = fig_data_c
        
        for column in df.columns.to_list():
            fig.add_trace(go.Scatter(x=df.index, y=df[column], name=column), row=1, col=1)
            
    elif plot_type == 'validation':
        fig_data = list(fig.data)
        fig_data_c = fig_data.copy()
        for i in range(len(fig_data)):
            if fig_data[i].xaxis == 'x2':
                fig_data_c.remove(fig_data[i])

        fig.data = fig_data_c
        
        for column in df.columns.to_list():
            fig.add_trace(go.Scatter(x=df.index, y=df[column], name=column), row=1, col=2)
#             fig.add_trace(go.Scatter(x=[], y=[], name=column), row=1, col=2)
    
#     fig['layout']['xaxis']['title']='Time'
#     fig['layout']['xaxis2']['title']='Time'
#     fig['layout']['yaxis']['title']='Value'
#     fig['layout']['yaxis2']['title']='Value'
    return fig