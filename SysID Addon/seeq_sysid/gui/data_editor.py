import plotly.graph_objects as go
import plotly.express as px
from pandas import DataFrame
import ipyvuetify as v
from copy import deepcopy


class DataEditor(v.Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fig = None
        self.df0 = DataFrame()
        self.df = DataFrame()
        
        self.cut_btn = v.Btn(children=[v.Icon(children=['mdi-content-cut'], small=True), 'Cut'], class_='mx-1', color='red darken-4', outlined=True)
        self.reset_btn = v.Btn(children=[v.Icon(children=['mdi-refresh'], small=True), 'Reset'], class_='mx-1', color='purple darken-4', outlined=True)
        self.done_btn = v.Btn(children=[v.Icon(children=['mdi-check'], small=True), 'Done'], color='success', class_='mx-1 mr-3', outlined=True)
        
        self.colors = px.colors.qualitative.Plotly
        
        self.cut_btn.on_event('click', self.cut_btn_action)
        self.reset_btn.on_event('click', self.reset_btn_action)

        fig = go.FigureWidget()
        fig.update_layout(
            dragmode='select',
            newshape_line_color='cyan',
        )
        fig.update_traces(marker=dict(size=3))
        fig['layout']['showlegend'] = True
        fig['layout']['xaxis']['rangeslider']['visible'] = False
        fig['layout']['xaxis']['title'] = 'Time'
        fig['layout']['margin']['t'] = 20
        fig['layout']['margin']['b'] = 35
        fig['layout']['margin']['r'] = 0
        fig['layout']['margin']['l'] = 0
        fig['layout']['modebar']['remove'] = ['Autoscale', 'zoomIn2d', 'zoomOut2d', 'toImage', 'lasso']
        
        fig['layout']['yaxis']['title'] = 'Value'
        fig['layout']['yaxis']['fixedrange'] = False
        
        
        self.blank_fig = fig
        self.fig = deepcopy(fig)
        
        self.class_='ma-5 pa-5 my-0'
        self.flat = True
        # self.width='60%'
        self.shaped=True
        self.children = [v.Row(children=[self.reset_btn, self.cut_btn, self.done_btn], class_='justify-end'), fig]

    def update_figure(self, df0: DataFrame):
        self.fig = deepcopy(self.blank_fig)
        self.df = df0.copy()
        
        fig_list = []
        
        for (tag_id, tag) in enumerate(self.df.columns):
            self.fig.add_trace(go.Scatter(x=self.df[tag].dropna().index, y=self.df[tag].dropna(), name=tag, mode='lines+markers',
                                          line=dict(color='rgba' + str(self.hex_to_rgba(h=self.colors[tag_id % 10],alpha=0.8))),
                                          selected_marker_color='black'))
            
        self.fig.update_traces(marker=dict(size=4))

        self.children = [v.Row(children=[self.reset_btn, self.cut_btn, self.done_btn], class_='justify-end'), self.fig]


    def cut_btn_action(self, item, *args):
        try:
            mins = []
            maxs = []
            for scat in self.fig.data:
                if scat.selectedpoints != ():
                    mins.append(min(scat.selectedpoints))
                    maxs.append(max(scat.selectedpoints))

            lb = min(mins)
            ub = max(maxs)

            self.df = self.df.drop(self.df.index[lb:ub+1])
            
            self.update_figure(self.df)
        except:
            pass
        
    def reset_btn_action(self, item, *args):
        self.df = self.df0.copy()
        self.update_figure(self.df)
        
    def hex_to_rgba(self, h, alpha):
        return tuple([int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)] + [alpha])
    
    def set_data(self, df0):
        self.df0 = df0.copy()
