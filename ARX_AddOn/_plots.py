import pandas as pd
import plotly
pd.options.plotting.backend = "plotly"


def df_plot(df):
    if df.empty:
#         df = pd.DataFrame()
#         fig = df.plot()
#         fig.data = []
        return None
    fig = df.plot()
    fig.layout.paper_bgcolor = 'rgba(0,0,0,0)'
    fig.layout.plot_bgcolor = 'rgba(0,0,0,0)'
    fig.layout.dragmode = "select"
    fig.layout.modebar = {
        'bgcolor': 'rgba(0, 0, 0, 0)',
        'color': 'rgba(221, 221, 221, 1)',
        'activecolor': 'rgba(0, 121, 96, 1)'
    }
    return fig

