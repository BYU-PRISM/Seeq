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
        
        self.min_ = []
        self.max_ = []

        fig = go.FigureWidget()

        fig['layout']['showlegend'] = False
        fig['layout']['xaxis']['rangeslider']['visible'] = True
        fig['layout']['xaxis']['title'] = 'Time'
        fig['layout']['margin']['t'] = 10
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
        
        eng_btn = v.Btn(children=['Eng'], style_='height:20pt')
        norm_btn = v.Btn(children=['Norm'], style_='height:20pt')
        self.units_switch = v.BtnToggle(children=[eng_btn,norm_btn],
                                             v_model=1,
                                             dense=True,
                                             tile=False,
                                             # rounded=True,
                                             mandatory=True,
                                             class_='ml-10 pl-10 pb-1 mt-3')
        self.units_switch.on_event('change', self.units_switch_action)

        train_item = v.TabItem(children=[self.units_switch, self.train_fig])
        validation_item = v.TabItem(children=[self.units_switch, self.validation_fig])
        
        # train_item = v.TabItem(children=[self.train_fig])
        # validation_item = v.TabItem(children=[self.validation_fig])

        figure_tabs = v.Tabs(children=[train_tab, validation_tab, train_item, validation_item], fixed_tabs=True,
                             color='#1d376c')
        self.children = [figure_tabs]

    def plot(self, train_df: DataFrame, validation_df: DataFrame):
        self.train_fig = deepcopy(self.blank_fig)
        self.validation_fig = deepcopy(self.blank_fig)

        range_ = self.max_ - self.min_

        tag_id = 0
        for idx, tag in enumerate(train_df.columns):
            y_train_norm = (train_df[tag].dropna().to_numpy() - self.min_[idx]) / range_[idx]
            self.train_fig.add_trace(go.Scatter(x=train_df[tag].dropna().index, y=y_train_norm, name=tag, visible=True,
                                                line=dict(color=self.colors[tag_id % 10])))
            tag_id += 1

        tag_id = 0
        for idx, tag in enumerate(validation_df.columns):
            y_validation_norm = (validation_df[tag].dropna().to_numpy() - self.min_[idx]) / range_[idx]
            self.validation_fig.add_trace(
                go.Scatter(x=validation_df[tag].dropna().index, y=y_validation_norm, name=tag, visible=True,
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
            
    def units_switch_action(self, *_):
        
        if len(self.min_):
            is_norm = self.units_switch.v_model

            range_ = self.max_ - self.min_

            if is_norm:  
                train_data = self.train_fig.data
                for idx, item in enumerate(train_data):
                    item['y'] = (item['y'] - self.min_[idx]) / range_[idx]

                validation_data = self.validation_fig.data
                for idx, item in enumerate(validation_data):
                    item['y'] = (item['y'] - self.min_[idx]) / range_[idx]

            else:
                train_data = self.train_fig.data
                for idx, item in enumerate(self.train_fig.data):
                    item['y'] = item['y']*range_[idx] + self.min_[idx]

                validation_data = self.validation_fig.data
                for idx, item in enumerate(self.validation_fig.data):
                    item['y'] = item['y']*range_[idx] + self.min_[idx]
