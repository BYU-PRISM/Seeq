import ipyvuetify as v

import plotly.graph_objects as go

from copy import deepcopy

class TransferCardResult(v.Dialog):
        
    def __init__(self,
                 dense=True,
                 class_='ma-4 pa-2',
                 style_='corner-radius:10px',
                 **kwargs):
                
        super().__init__(dense=dense,
                         style_=style_,
                         max_width='800px',
                         v_model=False,
                         overlay_opacity=0,
                         **kwargs)
        
        self.on_event('keydown.stop', lambda *args: None)

        self.model_equation = v.CardTitle(children=[], class_='ma-auto pa-auto pb-0 pt-0', align='top', dense=True)

        self.done_btn = v.Btn(children=['Done'], dark=True, color='success', class_='ma-0 pa-0 ml-4 mb-1', dense=True, no_gutters=True)
        
        self.card_switch = v.CardActions(children=[self.done_btn], no_gutters=True, class_='ma-auto pa-auto', dense=True)

        # Figure
        fig = go.FigureWidget()
        fig['layout']['showlegend'] = False
        fig['layout']['xaxis']['rangeslider']['visible'] = True
        fig['layout']['xaxis']['title'] = 'Time'
        fig['layout']['margin']['t'] = 10
        fig['layout']['margin']['b'] = 10
        fig['layout']['margin']['r'] = 10
        fig['layout']['margin']['l'] = 10

        fig['layout']['width'] = 480
        fig['layout']['height'] = 440

        fig['layout']['yaxis']['fixedrange'] = False
        
        self.blank_fig = fig
        self.fig = deepcopy(fig)
        self.fig_item = v.Card(children=[self.fig], style_='width:10%', class_='ma-auto pa-auto pt-0', elevation=0)


        # Model Properties
        self.model_prop_title = v.Text(children=['Model Properties: '], class_='mx-1 my-0 pt-2 pb-1', align='center', dense=True, style_='font-size:14pt; font-weight:bold')
        self.model_prop_item = v.Text(children=['Order: '], class_='ma-1 py-0 pl-4', align='center', dense=True, style_='font-size:12pt')
        
        # Step Information
        self.step_info_title = v.Text(children=['Step Info: '], class_='mx-1 my-0 pt-2 pb-1', align='center', dense=True, style_='font-size:14pt; font-weight:bold')
        self.step_info_item = v.Text(children=[v.Text(children=['Overshoot(%): ']), v.Text(children=['Rise Time: ']), v.Text(children=['Settling Time: '])],
                                     class_='d-flex flex-column ma-1 py-0 pl-4', align='center', dense=True, style_='font-size:13pt')
        
        
        self.model_info = v.Card(children=[self.model_prop_title, self.model_prop_item, self.step_info_title, self.step_info_item], 
                                 class_='d-flex flex-column justify-space-between',
                                 style_='width:35%',
                                 elevation=0)
        
        self.card_item = v.CardActions(children=[self.model_info, v.Spacer(), self.fig], style_='', class_='ma-0 pa-0 ml-2 align-start', elevation=0, disabled=False)

        self.dialog_card = v.Card(class_='pa-2', flat=True)
        self.dialog_card.children = [v.Row(children=[self.model_equation, v.Spacer(), self.card_switch], class_='pa-auto ma-auto mx-0', no_gutters=True, dense=True),
                       v.Divider(class_='mt-auto pt-auto mx-1 mb-2', dense=True),
                       self.card_item]
        self.children = [v.Card(children=[self.dialog_card])]
        
        
    def update_figure(self, df):
        self.fig.data = []
        
        self.fig['layout']['yaxis']['showticklabels'] = True
        step_plot = go.Scatter(x=df.index, y=df, line={'dash': 'solid'}, mode='lines')
        data = [step_plot]
        self.fig.add_traces(data)