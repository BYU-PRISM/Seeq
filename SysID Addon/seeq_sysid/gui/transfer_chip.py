import ipyvuetify as v

from seeq_sysid.gui.transfer_card_setup import TransferCardSetup
from seeq_sysid.gui.transfer_card_result import TransferCardResult
from seeq_sysid.gui.utils import create_eq
from copy import deepcopy

import plotly.graph_objects as go
from plotly.express.colors import qualitative


class TransferChip(v.Card):
    tmp_cv_name = None
    card_colors = qualitative.Plotly

    n_cv = 1
    def __init__(self, 
                 mv_name=None,
                 cv_name=None,
                 elevation = 0,
                 flat=True,
                 class_='ma-1 pa-0',
                 style_='font-size:10pt;  height:96px; width:170px'):
        
        super().__init__(class_=class_,
                         elevation=elevation,
                         flat=flat,
                         style_=style_)
        
        if TransferChip.tmp_cv_name is None:
            TransferChip.tmp_cv_name = cv_name
        elif TransferChip.tmp_cv_name != cv_name:
            TransferChip.tmp_cv_name = cv_name
            TransferChip.n_cv += 1
            
        self.color = TransferChip.card_colors[TransferChip.n_cv%10-1]
        
        self.cons_eqs = v.Col(children=[], class_='d-flex flex-column ma-0 pa-0 justify-center align-center mr-1', style_='width:60px ;font-size:8pt')

        self.tf_card: TransferCardSetup = TransferCardSetup(mv_name=mv_name, cv_name=cv_name)
        self.result_dialog = TransferCardResult()

        
        fig = go.FigureWidget()
        fig['layout']['showlegend'] = False
        fig['layout']['width'] = 90
        fig['layout']['height'] = 50
        fig['layout']['xaxis']['showticklabels'] = False
        fig['layout']['yaxis']['showticklabels'] = False 
        fig['layout']['margin']['t'] = 0
        fig['layout']['margin']['b'] = 0
        fig['layout']['margin']['r'] = 0
        fig['layout']['margin']['l'] = 0
        fig['layout']['modebar']['remove'] = ['Pan', 'Zoom', 'Autoscale', 'zoomIn2d', 'zoomOut2d', 'toImage', 'resetScale2d']
        fig['layout']['yaxis2'] = {'overlaying': 'y', 'side': 'right'}
        fig['layout']['yaxis2']['showticklabels'] = False
        fig['layout']['hovermode'] = False
        
        self.blank_fig = fig
        self.fig = deepcopy(self.blank_fig)
        
        self.mv_name = self.tf_card.mv_name
        self.cv_name = self.tf_card.cv_name
              
        self.status_icon = v.Icon(children=['mdi-check-circle'], color='success', dense=True)
        self.tf_chip_items = v.Card(children=[], dense=True, color='white', class_='d-flex flex-row justify-center align-center ma-1 pa-1 mr-0', style_='height:57px; width:160px')
        self.settings_icon = v.Icon(children=['mdi-settings'], class_='mdi-18px')
        self.loading_settings = v.Icon(children=['mdi-loading'], class_='mdi-18px mdi-spin')
        self.tf_card_btn = v.Btn(children=[self.settings_icon], color='white', v_on = 'menuData.on', dense=True, class_='d-flex ma-1 pa-1', style_='height:27px; width:160px')
        self.tf_card_btn.value = True
        self.tf_card_dialog = v.Menu(value=None, children=[self.tf_card], class_='ma-2 pa-2', close_on_content_click=False, v_slots=[{
                             'name': 'activator',
                             'variable': 'menuData',
                             'children': [self.tf_card_btn]
                         }],)
        
        self.update_title()
        self.update_summary()

        # Events
        # Model equation events
        self.tf_card.order_group.on_event('change', self.update_title)
        self.tf_card.gain_checkbox.on_event('change', self.gain_checkbox_action)
        self.tf_card.deadtime_checkbox.on_event('change', self.deadtime_checkbox_action)
        self.tf_card.ramp_checkbox.on_event('change', self.ramp_checkbox_action)
        self.tf_card.signal_on_off_switch.on_event('click', self.turn_off_tf_card)
        self.result_dialog.done_btn.on_event('click', self.close_result_dialog)
        
        # Summary Events
        self.tf_card_btn.on_event('click.right', self.turn_off_tf_card)
        
        
        # Constraints events
        self.tf_card.gain_lb.on_event('change', self.update_summary)
        self.tf_card.gain_ub.on_event('change', self.update_summary)
                
        self.tf_card.tau_lb.on_event('change', self.update_summary)
        self.tf_card.tau_ub.on_event('change', self.update_summary)
        
        self.tf_card.deadtime_lb.on_event('change', self.update_summary)
        self.tf_card.deadtime_ub.on_event('change', self.update_summary)
        
        
        """ Results Chip (Fliped) """
        # Step Response Figure
        self.step_fig = None
        self.create_step_figure()
        
        # Model Info Summary
        # Gain
        self.gain_text = v.Row(children=[''], style_='font-size:12pt', class_='d-flex justify-space-between')
        # Time Constant (tau)
        self.tau_text = v.Row(children=[''], style_='font-size:12pt', class_='d-flex justify-space-between')
        # Time Delay (theta)
        self.theta_text = v.Row(children=[''], style_='font-size:12pt', class_='d-flex justify-space-between')    
        # Damping value (zeta)
        self.zeta_text = v.Row(children=[''], style_='font-size:12pt', class_='d-flex justify-space-between') 
        
        # Step Response Summary
        # Zeta Type (under damped, damped, over damped)
        self.zeta_cat = None
        self.zeta_cat_text = v.Row(children=[''], style_='font-size:12pt', class_='d-flex justify-space-between')
        # settling time
        self.ts = None
        self.ts_text = v.Row(children=[''], style_='font-size:12pt', class_='d-flex justify-space-between')
        # rise time
        self.tr = None
        self.tr_text = v.Row(children=[''], style_='font-size:12pt', class_='d-flex justify-space-between')
        # overshoot
        self.os = None
        self.os_text = v.Row(children=[''], style_='font-size:12pt', class_='d-flex justify-space-between')
        
        # Transfer function visualization
        self.order = None   
        self.gain_gui = None
        self.tau_gui = None
        self.theta_gui = None
        self.zeta_gui = None  
        
        self.step_info = v.Col(children=[], class_='d-flex flex-column ma-0 pa-0 justify-center align-center', style_='width:100% ;font-size:8pt', dense=True)
        self.fraction_col = v.Col(children=[], class_='d-flex flex-column ma-0 pa-0 py-1 justify-center align-center', style_='width:100% ;font-size:10pt', dense=True)
        self.model_equation = v.Card(children=[], class_='d-flex flex-row justify-center align-center ma-0 pa-0 mx-1',
                                     style_='height:30px; max-width:100%; font-size:7pt', elevation=0, flat=True, dense=True)
        
        self.info_fig = v.Card(children=[self.step_info, self.step_fig],
                               dense=True, color='white',
                               class_='d-flex flex-row justify-center align-center pa-0 ma-0 mt-1 pt-1',
                               style_='height:57px; width:160px', elevation=0, flat=True)
        
        self.results_card = v.Card(children=[self.info_fig], class_='ma-1 pa-1 pt-0 pr-0 justify-center align-center', dense=True)
        self.results_card.on_event('click', self.result_dialog_action)
        
        self.no_solution_card = v.Card(children=['No Solution Found'],
                                       dense=True, color='white', 
                                       class_='d-flex justify-center align-center pa-0 ma-0 mt-1 pt-1 ml-1 pl-1',
                                       style_='height:87px; width:160px')

        
        self.children = [self.tf_chip_items, self.tf_card_btn, self.tf_card_dialog]
        
    def turn_off_tf_card(self, *args):
        self.tf_card_btn.value = not self.tf_card_btn.value
        self.tf_card.signal_on_off_switch.v_model = not self.tf_card.signal_on_off_switch.v_model
        self.update_summary()
        
        if self.tf_card_btn.value:
            self.status_icon.color = 'success'
            self.status_icon.children=['mdi-check-circle']

            self.tf_card_btn.color = 'white'
            self.mode_select_action(self.tf_card.signal_on_off_switch)
            self.update_summary()
            self.tf_chip_items.children = [self.cons_eqs, self.fig]
            self.children = [self.tf_chip_items, self.tf_card_btn, self.tf_card_dialog]
            self.tf_chip_items.color = 'white'
            
        else:
            self.status_icon.color = 'red lighten-1'
            self.status_icon.children = ['mdi-close-circle']
            
            self.tf_card_btn.color = 'grey lighten-2'
            self.mode_select_action(self.tf_card.signal_on_off_switch)
            self.tf_chip_items.children = ['Inactive']
            self.tf_chip_items.color = 'grey lighten-2'

            
    def mode_select_action(self, item, *_):
        switch_values = ['Off', 'On']
        item.label = switch_values[item.v_model]
        
        self.tf_card.order_group.disabled = not item.v_model
        self.tf_card.ramp_checkbox.disabled = not item.v_model
        self.tf_card.gain_checkbox.disabled = not item.v_model
        self.tf_card.deadtime_checkbox.disabled = not item.v_model
        self.tf_card.gain_lb.disabled = not item.v_model
        self.tf_card.gain_ub.disabled = not item.v_model
        self.tf_card.tau_lb.disabled = not item.v_model
        self.tf_card.tau_ub.disabled = not item.v_model
        self.tf_card.deadtime_lb.disabled = not item.v_model
        self.tf_card.deadtime_ub.disabled = not item.v_model
        
        
    def update_summary(self, *args):       
        gain_lb = self.tf_card.gain_lb.v_model
        gain_ub = self.tf_card.gain_ub.v_model
        
        tau_lb = self.tf_card.tau_lb.v_model
        tau_ub = self.tf_card.tau_ub.v_model
        
        deadtime_lb = self.tf_card.deadtime_lb.v_model
        deadtime_ub = self.tf_card.deadtime_ub.v_model
        
        order = self.tf_card.order_group.v_model
        
        order_info = ''
        gain_info = ''
        tau_info = ''
        deadtime_info = ''
        children_list = []
        
        if order == 1:
            # order_eq = create_eq('FOPDT', 'black', '1.5pt', '0pt', '0pt')
            order_eq = v.Text(children=['FOPDT'], class_='ma-0 pa-0', style_='font-size:7pt; max-height:11px')
            children_list.append(order_eq)
        elif order == 2:
            order_eq = v.Text(children=['SOPDT'], class_='ma-0 pa-0', style_='font-size:7pt; max-height:11px')
            children_list.append(order_eq)
            
        if self.tf_card.gain_checkbox.v_model:
            gain_info = ' k '
            if len(gain_lb) > 0:
                gain_info = 'lb < ' + gain_info
                
            if len(gain_ub) > 0:
                gain_info = gain_info + ' < ub'
        else:
            gain_info = 'k = 1'

        gain_eq = v.Text(children=[gain_info], class_='ma-0 pa-0', style_='font-size:7pt; max-height:11px')
        children_list.append(gain_eq)
            
            
        if not self.tf_card.ramp_checkbox.v_model:
            tau_info = ' tau '
            if len(tau_lb) > 0:
                tau_info = 'lb < ' + tau_info
                
            if len(tau_ub) > 0:
                tau_info = tau_info + ' < ub'
        else:
            tau_info = 'Ramp'
        
        tau_eq = v.Text(children=[tau_info], class_='ma-0 pa-0', style_='font-size:7pt; max-height:11px')
        children_list.append(tau_eq)
            
            
        if self.tf_card.deadtime_checkbox.v_model:
            deadtime_info = ' dt '
            if len(deadtime_lb) > 0:
                deadtime_info = 'lb < ' + deadtime_info
                
            if len(deadtime_ub) > 0:
                deadtime_info = deadtime_info + ' < ub'
        else:
            deadtime_info = 'No DT'

        deadtime_eq = v.Text(children=[deadtime_info], class_='ma-0 pa-0', dense=True, style_='font-size:7pt; max-height:11px')

        children_list.append(deadtime_eq)

        
        self.cons_eqs.children = children_list
        self.tf_chip_items.children = [self.cons_eqs, self.fig]
    
    def update_title(self, *args):
        gain = self.tf_card.gain_checkbox.v_model
        deadtime = self.tf_card.deadtime_checkbox.v_model
        ramp = self.tf_card.ramp_checkbox.v_model
        order = self.tf_card.order_group.v_model
        
        k = ''
        den = ''
        theta = ''
        
        if order == 1:
            if gain:
                k = 'k_p'
            if deadtime:
                theta = 'e^{-\\theta_p s}'

            if (gain+deadtime)==0:
                k = '1'
            if ramp:
                den = 's'
            else:
                den = '\\tau_p s+1'
                
        elif order == 2:
            if gain:
                k = 'k_p'
            if deadtime:
                theta = 'e^{-\\theta_p s}'      
            if (gain+deadtime)==0:
                k = '1'
            if ramp:
                den = 's^2'
            else:
                den = '(\\tau_p s)^2+ 2 \\tau_p \\zeta s+1'
        
        tf_formula = '$\\frac{%s(s)}{%s(s)}=\\frac{%s %s}{%s}$' % (self.cv_name, self.mv_name, k, theta, den)
        self.tf_card.card_name.children = [create_eq(tf_formula, 'black', '4pt', '1pt', '1pt')]
        
        self.update_summary()
        
    def gain_checkbox_action(self, item, *args):
        self.tf_card.gain_lb.disabled = not item.v_model
        self.tf_card.gain_ub.disabled = not item.v_model
        self.update_title()
    
    def ramp_checkbox_action(self, item, *args):
        self.tf_card.tau_lb.disabled = item.v_model
        self.tf_card.tau_ub.disabled = item.v_model
        self.update_title()

    def deadtime_checkbox_action(self, item, *args):
        self.tf_card.deadtime_lb.disabled = not item.v_model
        self.tf_card.deadtime_ub.disabled = not item.v_model
        self.update_title()
        
    def close_tf_card(self, item, *args):
        self.tf_card_dialog.value = False
        
    def close_result_dialog(self, item, *args):
        self.result_dialog.v_model = None
    
    def update_meas_figure(self, df):
        self.tf_card.update_figure(df)
        self.fig = deepcopy(self.blank_fig)
        cv_plot = go.Scatter(x=df.index, y=df[self.cv_name], name=self.cv_name, yaxis='y1')
        mv_plot = go.Scatter(x=df.index, y=df[self.mv_name], name=self.mv_name, yaxis='y2', line={'dash': 'dot'})
        data = [cv_plot, mv_plot]
        self.fig.add_traces(data)
        
        self.tf_chip_items.children = [self.cons_eqs, self.fig]
        self.children = [self.tf_chip_items, self.tf_card_btn, self.tf_card_dialog]
        
    def compile_item(self):
        item = self.tf_card
        self.order = item.order_group.v_model
        self.no_gain = not item.gain_checkbox.v_model
        self.no_ramp = not item.ramp_checkbox.v_model
        self.is_dt = item.deadtime_checkbox.v_model
        
        gain_lb = item.gain_lb.v_model
        gain_ub = item.gain_ub.v_model
        
        tau_lb = item.tau_lb.v_model
        tau_ub = item.tau_ub.v_model
        
        deadtime_lb = item.deadtime_lb.v_model
        deadtime_ub = item.deadtime_ub.v_model
        
        # Gain
        self.gain_lb = float(gain_lb) if len(gain_lb) > 0 else None
        self.gain_ub = float(gain_ub) if len(gain_ub) > 0 else None
             
        # Time Constant
        self.tau_lb = float(tau_lb) if len(tau_lb) > 0 else None
        self.tau_ub = float(tau_ub) if len(tau_ub) > 0 else None
        
        # Deadtime
        self.deadtime_lb = float(deadtime_lb) if len(deadtime_lb) > 0 else None
        self.deadtime_ub = float(deadtime_ub) if len(deadtime_ub) > 0 else None
        
    
    
    """ Result Functions """
    def update_info(self): 
        # Create model prop
        self.gain_text.children = [v.Text(children=['Gain(K)'], style_='font-weight:bold'), v.Text(children=[' {:.5} '.format(self.gain_gui)] )] if self.gain_gui else []
        self.tau_text.children = [v.Text(children=['Time Constant(tau)'], style_='font-weight:bold'), v.Text(children=[' {:.5} s'.format(self.tau_gui)] )] if self.tau_gui else []
        self.theta_text.children = [v.Text(children=['Time Delay(theta)'], style_='font-weight:bold'), v.Text(children=[' {:.5} s'.format(self.theta_gui)] )] if self.theta_gui else []
        
        if self.order == 2:
            self.zeta_text.children = [v.Text(children=['Relative Damping:'], style_='font-weight:bold'), v.Text(children=[' {:.5} '.format(self.zeta_gui)])] if self.tau_gui else []
            
        self.result_dialog.model_prop_item.children = [self.gain_text, self.tau_text, self.theta_text, self.zeta_text]
              

        # Create step info
        self.ts_text.children = [v.Text(children=['Settling Time:'], style_='font-weight:bold'), v.Text(children=[' {:.5} s'.format(self.ts)] )] if self.ts else [v.Text(children=['Settling Time:'], style_='font-weight:bold'), v.Text(children=['NA'] )]
        self.tr_text.children = [v.Text(children=['Rise Time:'], style_='font-weight:bold'), v.Text(children=[' {:.5} s'.format(self.tr)] )] if self.tr else [v.Text(children=['Rise Time:'], style_='font-weight:bold'), v.Text(children=['NA'] )]
        self.os_text.children = [v.Text(children=['Overshoot:'], style_='font-weight:bold'), v.Text(children=[' {:.4} %'.format(float(self.os))] )]
        if self.order == 2:
            if (0.999 <= self.zeta_gui <= 1.001): 
                self.zeta_cat = v.Text(children=['Critically Damped'])
            elif (self.zeta_gui < 0.999):
                self.zeta_cat = v.Text(children=['Underdamped'])
            elif (self.zeta_gui > 1.001):
                self.zeta_cat = v.Text(children=['Overdamped'])
                
            self.zeta_cat_text.children = [v.Text(children=['Response Type:'], style_='font-weight:bold'), self.zeta_cat]

        self.result_dialog.step_info_item.children = [self.zeta_cat_text, self.ts_text, self.tr_text, self.os_text]
        
        # Create tf Equation
        num_str = ''
        num_str += '{0:.3}'.format(float(self.gain_gui)) if self.gain_gui else ''
        num_str += '  e^{{-{0:.3} s}}'.format(float(self.theta_gui)) if self.theta_gui else ''
        num_str = '1' if len(num_str) == 0 else num_str

        if self.order == 1:
            den_str = ''
            den_str += '{0:.5} s+1'.format(float(self.tau_gui)) if self.tau_gui else 's'

        elif self.order == 2:
            den_str = ' + {0:.5} s+1'.format(float(2*self.zeta_gui*self.tau_gui)) if (self.zeta_gui and self.tau_gui) else '+1'
            den_str = ('{0:.5} s^2'.format(float(self.tau_gui**2))+den_str) if self.tau_gui else 's^2'

        elif self.order == None:
            numerator = ''
            denominator = ''
        
        eq = '$ \\frac{%s}{%s} $' % (num_str, den_str)
        eq_widget = create_eq(eq, 'black', '4pt', '0pt', '0pt')
        self.fraction_col.children= [eq_widget]
        
        return ['G(s) = ', self.fraction_col]
    
    def update_result_dialog(self, df=None):
        self.result_dialog.model_equation.children = self.update_info()
        self.create_step_figure(df)
        
    def create_step_figure(self, df=None):
        fig: go.FigureWidget = deepcopy(self.blank_fig)
        fig['layout']['dragmode'] = False
        fig['layout']['width'] = 155
        fig['layout']['height'] = 84
        
        fig['layout']['margin']['t'] = 5
        fig['layout']['margin']['b'] = 0
        fig['layout']['margin']['r'] = 2
        fig['layout']['margin']['l'] = 2
        
        fig['layout']['xaxis']['showgrid'] = False
        fig['layout']['xaxis']['showticklabels'] = True
        fig['layout']['xaxis']['tickfont_size'] = 8
        fig['layout']['xaxis']['ticks'] = 'inside'
        
        fig['layout']['yaxis']['showgrid'] = False
        fig['layout']['yaxis']['showticklabels'] = True 
        fig['layout']['yaxis']['tickfont_size'] = 8
        fig['layout']['yaxis']['ticks'] = 'inside'

        self.step_fig = fig
        
        if df is not None:
            # Create Fig for Chip
            step_plot = go.Scatter(x=df.index, y=df[self.cv_name+'_tf'], name=self.cv_name+'_tf', yaxis='y1', line={'dash': 'solid'}, mode='lines')
            data = [step_plot]
            self.step_fig.add_traces(data)
            
            # Create Fig for Dialog
            self.result_dialog.update_figure(df[self.cv_name+'_tf'])
    
    def switch_chip(self):
        self.results_card.children = [self.step_fig]
        self.children = [self.results_card, self.result_dialog]
        
    def result_dialog_action(self, item, *args):
        self.result_dialog.v_model = True
        

    # Reset ns
    @staticmethod
    def reset():
        TransferChip.n_cv = 1
