import ipyvuetify as v

import plotly.graph_objects as go


class TransferCardSetup(v.Card):
    
    item_id = 0
    
    def __init__(self,
                 mv_name=None,
                 cv_name=None,
                 dense=True,
                 elevation=3,
                 class_='ma-0 px-4 pt-1 pb-3',
                 style_='max-width:600px; corner-radius:10px',
                 shaped=False,
                 flat=False,
                 **kwargs):
        
        if mv_name:
            self.mv_name = mv_name
        else:
            self.mv_name = 'MV'+str(TransferCardSetup.item_id) 
            
        if cv_name:
            self.cv_name = cv_name
        else:
            self.cv_name = 'CV'+str(TransferCardSetup.item_id) 
                
        super().__init__(dense=dense,
                         elevation=elevation,
                         class_=class_,
                         style_=style_,
                         shaped=shaped,
                         flat=flat,
                         **kwargs)

        self.card_name = v.CardTitle(children=[self.mv_name], class_='ma-auto pa-auto pb-0 pt-0', align='top', dense=True)

        self.done_btn = v.Btn(children=['Done'], dark=True, color='success', class_='ma-0 pa-0 ml-4 mb-1', dense=True, no_gutters=True)
        
        signal_switch_list = ['Off', 'On']
        self.signal_on_off_switch = v.Switch(inset=True, class_='ma-0 pa-0 mt-4', v_model=True, label='On', color='success', dark=False, no_gutters=True, dense=True, ripple=False, height='0px')
        self.signal_on_off_switch.label = signal_switch_list[self.signal_on_off_switch.v_model]

        self.card_switch = v.CardActions(children=[self.signal_on_off_switch], no_gutters=True, class_='ma-auto pa-auto', dense=True)


        # Figure
        fig = go.FigureWidget()
        fig['layout']['showlegend'] = False
        fig['layout']['margin']['t'] = 10
        fig['layout']['margin']['b'] = 10
        fig['layout']['margin']['r'] = 0
        fig['layout']['margin']['l'] = 10

        fig['layout']['width'] = 280
        fig['layout']['height'] = 240

        fig['layout']['yaxis']['fixedrange'] = False
        
        self.fig = fig
        self.fig_item = v.Card(children=[self.fig], style_='width:10%', class_='ma-auto pa-auto pt-0', elevation=0)


        # Radio Buttons
        self.order_group = v.RadioGroup(label='Order:', v_model=1, class_='mx-1 my-0 py-0', align='center', dense=True)
        self.radio_fopdt = v.Radio(label='FOPDT', v_model=1, color='blue darken-4', ripple=False, class_='my-0', dense=True)
        self.radio_sopdt = v.Radio(label='SOPDT', v_model=2, color='blue darken-4', ripple=False, class_='my-0', dense=True)
        self.order_group.children = [self.radio_fopdt, self.radio_sopdt]


        # checkboxes
        self.ramp_checkbox = v.Checkbox(label='Ramp', color='blue darken-4', class_='ma-auto pa-0 ml-0', dense=True, ripple=False, v_model=False, height='9px')
        self.gain_checkbox = v.Checkbox(label='Gain', color='blue darken-4', class_='ma-auto pa-0 ml-0', dense=True, ripple=False, v_model=True, height='9px')
        self.deadtime_checkbox = v.Checkbox(label='Deadtime', color='blue darken-4', class_='ma-auto pa-0 ml-0', dense=True, ripple=False, v_model=False, height='9px')
        
        self.options_group = v.Card(children=[self.gain_checkbox, self.deadtime_checkbox, self.ramp_checkbox],
                         no_gutters=True,
                         dense=True, 
                         class_='ma-auto pa-auto mt-1 ml-2 mb-0 pb-0 mr-6 pr-3',
                         elevation=0)
        
        # Constraints
        self.gain_lb = v.TextField(label='lb', v_model='', class_='ml-3 mt-0 pt-0', dense=True, style_='max-width:20%')
        self.gain_ub = v.TextField(label='ub', v_model='', class_='ml-3 mt-0 pt-0', dense=True, style_='max-width:20%')
        self.gain_limit = v.Card(children=['Gain:', v.Spacer(), self.gain_lb, self.gain_ub],
                                 class_='d-flex d-row justify-right align-center mr-3 mt-0 pt-0',
                                 style_='font-size:12pt',
                                 elevation=0, flat=True)

        self.tau_lb = v.TextField(label='lb', v_model='0', class_='ml-3 mt-0 pt-0', dense=True, style_='max-width:20%')
        self.tau_ub = v.TextField(label='ub', v_model='', class_='ml-3 mt-0 pt-0', dense=True, style_='max-width:20%')
        self.tau_limit = v.Card(children=['Time Constant:', v.Spacer(), self.tau_lb, self.tau_ub],
                                class_='d-flex d-row justify-right align-center mr-3 mt-0 pt-0',
                                style_='font-size:11pt',
                                elevation=0, flat=True)
        
        self.deadtime_lb = v.TextField(label='lb', v_model='0', class_='ml-3 mt-0 pt-0', dense=True, style_='max-width:20%', disabled=True)
        self.deadtime_ub = v.TextField(label='ub', v_model='', class_='ml-3 mt-0 pt-0', dense=True, style_='max-width:20%', disabled=True)
        self.deadtime_limit = v.Card(children=['Deadtime:', v.Spacer(), self.deadtime_lb, self.deadtime_ub],
                                     class_='d-flex d-row justify-right align-center mr-3 mt-0 pt-0',
                                     style_='font-size:11pt', elevation=0, flat=True)

        self.constraints_card = v.Card(class_='ma-auto pa-auto mt-0', elevation=0, flat=True, dense=True)
        self.constraints_card.children = [self.gain_limit, self.tau_limit, self.deadtime_limit]
        self.tf_struct_options = v.Card(children=[self.order_group, v.Spacer(), self.options_group],
                                 no_gutters=True,
                                 dense=True, 
                                 class_='d-flex flex-row ma-auto pa-0 mt-3',
                                 elevation=0)
        
        self.tf_options = v.Card(children=[self.tf_struct_options, self.constraints_card], class_='', elevation=0)

        self.card_item = v.CardActions(children=[self.tf_options, v.Spacer(), self.fig], style_='', class_='ma-0 pa-0 ml-2', elevation=0, disabled=False)

        self.children=[v.Row(children=[self.card_name, v.Spacer(), self.card_switch],
                             class_='pa-auto ma-auto mx-0', 
                             no_gutters=True, dense=True),
                       v.Divider(class_='mt-auto pt-auto mx-1 mb-2', dense=True),
                       self.card_item]
        
        TransferCardSetup.item_id += 1
        
    def update_figure(self, df):
        self.fig['layout']['yaxis2'] = {'overlaying': 'y', 'side': 'right'}
        self.fig['layout']['yaxis']['showticklabels'] = True
        self.fig['layout']['yaxis2']['showticklabels'] = True
        cv_plot = go.Scatter(x=df.index, y=df[self.cv_name], name=self.cv_name, yaxis='y1')
        mv_plot = go.Scatter(x=df.index, y=df[self.mv_name], name=self.mv_name, yaxis='y2', line={'dash': 'dash'})
        data = [cv_plot, mv_plot]
        self.fig.add_traces(data)

        
        
    # Reset Item ID
    @staticmethod
    def reset():
        TransferCardSetup.item_id = 0
