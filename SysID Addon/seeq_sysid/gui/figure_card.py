from copy import deepcopy

import ipyvuetify as v
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame


# Figures Tabs (Train+Validation) Class
class FigureCard(v.Card):
    def __init__(self,
                 width='100%',
                 height='100%',
                 elevation=5,
                 shaped=True,
                 outlined=False,
                 color='white',
                 class_='mt-4 pa-4',
                 **kwargs):

        super().__init__(
            width=width,
            # height=height,
            elevation=elevation,
            shaped=shaped,
            outlined=outlined,
            color=color,
            class_=class_,
            **kwargs)

        fig = go.FigureWidget()

        fig['layout']['showlegend'] = False
        fig['layout']['xaxis']['rangeslider']['visible'] = True
        fig['layout']['xaxis']['title'] = 'Time'
        fig['layout']['margin']['t'] = 30
        fig['layout']['margin']['b'] = 40
        fig['layout']['margin']['r'] = 0
        fig['layout']['yaxis']['title'] = 'Value'
        fig['layout']['yaxis']['fixedrange'] = False

        self.colors = px.colors.qualitative.Plotly

        self.blank_fig = fig
        self.train_fig = deepcopy(self.blank_fig)
        self.validation_fig = deepcopy(self.blank_fig)

        self.create_figure()

    def create_figure(self):
        train_tab = v.Tab(children=['Train'], style_='font-weight:bold')
        validation_tab = v.Tab(children=['Validation'], style_='font-weight:bold')

        train_item = v.TabItem(children=[self.train_fig])
        validation_item = v.TabItem(children=[self.validation_fig])

        figure_tabs = v.Tabs(children=[train_tab, validation_tab, train_item, validation_item], fixed_tabs=True,
                             color='#1d376c')
        self.children = [figure_tabs]

    def plot(self, train_df: DataFrame, validation_df: DataFrame):
        self.train_fig = deepcopy(self.blank_fig)
        self.validation_fig = deepcopy(self.blank_fig)

        tag_id = 0
        for tag in train_df.columns:
            self.train_fig.add_trace(go.Scatter(x=train_df[tag].dropna().index, y=train_df[tag].dropna(), name=tag, visible=False,
                                                line=dict(color=self.colors[tag_id % 10])))
            tag_id += 1

        tag_id = 0
        for tag in validation_df.columns:
            self.validation_fig.add_trace(
                go.Scatter(x=validation_df[tag].dropna().index, y=validation_df[tag].dropna(), name=tag, visible=False,
                           line=dict(color=self.colors[tag_id % 10])))
            tag_id += 1

        self.create_figure()

    def update(self, idx: int, status: bool = None, line_style: str = None):
        if status is not None:
            self.train_fig.data[idx].visible = status
            self.validation_fig.data[idx].visible = status

        if line_style:
            self.train_fig.data[idx].line['dash'] = line_style
            self.validation_fig.data[idx].line['dash'] = line_style
