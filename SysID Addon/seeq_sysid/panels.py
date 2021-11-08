# Import Packages

import ipyvuetify as v
import plotly.express as px

from seeq_sysid.left_panel import Left_Panel
from seeq_sysid.utils import create_eq


# ARX Model Panel
class Arx_Panel(Left_Panel):
    def __init__(self, *args, **kwargs):
        model_name = 'ARX'
        super().__init__(model_name=model_name,
                         *args, **kwargs)

        # Icons
        title_icon = v.Icon(class_='', children=['mdi-tools'], color='white')

        # Expanding Panel
        # ARX Model Order
        self.na_min = v.TextField(label='min', v_model='2', dense=True, class_='pl-2', color='white', dark=True,
                                  style_='width:35px')
        self.na_max = v.TextField(label='max', v_model='2', dense=True, class_='pl-2', color='white', dark=True,
                                  style_='width:35px')
        self.na = v.Row(
            children=[v.Row(children=['Auto-Regressive', create_eq('$(n_a):$', 'white', 2, top='0px')], class_='mt-0'),
                      self.na_min, self.na_max],
            class_='',
            dense=True,
            style_='font-weight:bold; color:white; font-size:13px', align='center')

        self.nb_min = v.TextField(label='min', v_model='2', dense=True, class_='pl-2', color='white', dark=True,
                                  style_='width:35px', align='top')
        self.nb_max = v.TextField(label='max', v_model='2', dense=True, class_='pl-2', color='white', dark=True,
                                  style_='width:35px', align='top')
        self.nb = v.Row(
            children=[v.Row(children=['Exogenous Input', create_eq('$(n_b):$', 'white', 2, top='0px')], class_='mt-0'),
                      self.nb_min, self.nb_max],
            class_='',
            dense=True,
            style_='font-weight:bold; color:white; font-size:13px', align='center')

        self.nk_min = v.TextField(label='min', v_model='0', dense=True, class_='pl-2', color='white', dark=True,
                                  style_='width:5px')
        self.nk_max = v.TextField(label='max', v_model='0', dense=True, class_='pl-2', color='white', dark=True,
                                  style_='width:5px')
        self.nk = v.Row(children=[v.Row(children=['Input Delay', create_eq('$(n_k):$', 'white', 2, top='0px')],
                                        class_='d-flex justify-right'), self.nk_min, self.nk_max],
                        class_='d-flex justify-right',
                        dense=True,
                        style_='font-weight:bold; color:white; font-size:13px', align='center')

        self.orders_panel_obj = v.ExpansionPanel(children=[
            v.ExpansionPanelHeader(children=['Model Order'],
                                   style_='font-weight:bold; color:white; font-size:12pt',
                                   dense=True,
                                   align='center',
                                   dark=True),
            v.ExpansionPanelContent(
                children=[v.Col(children=[self.na, self.nb, self.nk],
                                style_='font-size:14px; font-weight:bold',
                                dark=True,
                                align='center',
                                class_='',
                                dense=True)])],
            style_='background-color:#007960')

        self.orders_panel = v.ExpansionPanels(children=[self.orders_panel_obj], dense=True, style_='width: 300px',
                                              flat=False)
        self.orders_layout = v.Layout(children=[self.orders_panel], class_='mb-6', dense=True, flat=False)

        # Arx
        self.title = v.Card(class_='pt-5 mb-7 mx-0 d-flex justify-left', style_='font-size:20px; background:none',
                            dark=True, center=True, align='center', flat=True,
                            children=[title_icon, v.Divider(vertical=True, class_='mx-2'),
                                      "{} Settings".format(self.model_name)])

        self.children = [self.title,
                         'Manipulated Variables (MV)', self.mv_select,
                         'Measured Variables (CV)', self.cv_select,
                         self.orders_layout,
                         v.Divider(class_='mb-4'),
                         'Training Conditions', self.train_condition,
                         'Validation Conditions', self.validation_condition,
                         v.Divider(class_='mb-6'),
                         self.identify_push_card]


# State-Space Panel
class SS_Panel(Left_Panel):
    def __init__(self, *args, **kwargs):
        model_name = 'Subspace'
        super().__init__(model_name=model_name,
                         *args, **kwargs)

        # Icons
        title_icon = v.Icon(class_='', children=['mdi-tools'], color='white')

        # Drop Downs
        self.method_select = v.Select(tag='Methods',
                                      v_model='DMDc',
#                                       items=['N4SID', 'DMDc'],
                                      items=['DMDc'],
                                      color=self.colors['seeq_primary'],
                                      item_color=self.colors['seeq_primary'],
                                      dense=True,
                                      outlined=True,
                                      class_='d-flex justify-center',
                                      style_='width: 280px; font-size:14px',
                                      filled=True,
                                      background_color='white',
                                      placeholder='Select',
                                      multiple=False)

        self.method_select.on_event('change', self.method_select_action)

        # Expanding Panel
        # State-Space Model Residual Energy Threshold
        self.method_box = None
        self.threshold_box = v.TextField(label='epsilon', v_model='1e-6', dense=True, class_='pl-2 pt-1', color='white',
                                         dark=True, style_='width:70px; font-size:11pt', hint='ex: 1e-6')
        self.threshold = v.Row(
            children=[v.Row(children=['Threshold'], class_='mt-0', style_='font-size:11pt; font-weight:bold'),
                      self.threshold_box],
            class_='',
            dense=True,
            style_='font-weight:bold; color:white; font-size:13px', align='center')

        self.order_box = v.TextField(label='Order', v_model='4', dense=True, class_='pl-2 pt-1', color='white',
                                     dark=True, style_='width:70px; font-size:11pt', hint='ex: 4')
        self.order = v.Row(children=[
            v.Row(children=['States', create_eq('$(n):$', 'white', 2, top='0px')], class_='mt-0',
                  style_='font-size:11pt; font-weight:bold'), self.order_box],
            class_='',
            dense=True,
            style_='font-weight:bold; color:white; font-size:13px', align='center')

        self.method_box = self.threshold

        self.orders_panel_obj = v.ExpansionPanel(
            children=[v.ExpansionPanelHeader(children=['Model Order'],
                                             style_='font-weight:bold; color:white; font-size:12pt',
                                             dense=True,
                                             align='center',
                                             dark=True),
                      v.ExpansionPanelContent(
                          children=[v.Col(children=[self.method_box],
                                          style_='font-size:14px; font-weight:bold',
                                          dark=True,
                                          align='center',
                                          dense=True)])],
            style_='background-color:#007960')

        self.orders_panel = v.ExpansionPanels(children=[self.orders_panel_obj], dense=True, style_='width: 300px',
                                              flat=False)
        self.orders_layout = v.Layout(children=[self.orders_panel], class_='mb-6', dense=True, flat=False)

        # Sub-Space
        self.title = v.Card(class_='pt-5 mb-7 mx-0 d-flex justify-left', style_='font-size:20px; background:none',
                            dark=True, center=True, align='center', flat=True,
                            children=[title_icon, v.Divider(vertical=True, class_='mx-2'),
                                      '{} Settings'.format(self.model_name)])

        self.children = [self.title,
                         'Manipulated Variables (MV)', self.mv_select,
                         'Measured Variables (CV)', self.cv_select,
                         'Method', self.method_select,
                         self.orders_layout,
                         v.Divider(class_='mb-4'),
                         'Training Conditions', self.train_condition,
                         'Validation Conditions', self.validation_condition,
                         v.Divider(class_='mb-6'),
                         self.identify_push_card]

    def method_select_action(self, item, *_):
        if item.v_model == 'N4SID':
            self.method_box = self.threshold
            self.orders_panel_obj = v.ExpansionPanel(children=[
                v.ExpansionPanelHeader(children=['Model Order'],
                                       style_='font-weight:bold; color:white; font-size:12pt',
                                       dense=True,
                                       align='center',
                                       dark=True),
                v.ExpansionPanelContent(
                    children=[v.Col(children=[self.method_box],
                                    style_='font-size:14px; font-weight:bold',
                                    dark=True,
                                    align='center',
                                    dense=True)])],
                style_='background-color:#007960')

            self.orders_panel = v.ExpansionPanels(children=[self.orders_panel_obj], dense=True, style_='width: 300px',
                                                  flat=False)
            self.orders_layout = v.Layout(children=[self.orders_panel], class_='mb-6', dense=True, flat=False)
            self.children = [self.title,
                             'Manipulated Variables (MV)', self.mv_select,
                             'Measured Variables (CV)', self.cv_select,
                             'Method', self.method_select,
                             self.orders_layout,
                             v.Divider(class_='mb-4'),
                             'Training Conditions', self.train_condition,
                             'Validation Conditions', self.validation_condition,
                             v.Divider(class_='mb-6'),
                             self.identify_push_card]

        elif item.v_model == 'DMDc':
            self.method_box = self.order
            self.orders_panel_obj = v.ExpansionPanel(children=[
                v.ExpansionPanelHeader(children=['Model Order'],
                                       style_='font-weight:bold; color:white; font-size:12pt',
                                       dense=True,
                                       align='center',
                                       dark=True),
                v.ExpansionPanelContent(
                    children=[v.Col(children=[self.method_box],
                                    style_='font-size:14px; font-weight:bold',
                                    dark=True,
                                    align='center',
                                    dense=True)])],
                style_='background-color:#007960')

            self.orders_panel = v.ExpansionPanels(children=[self.orders_panel_obj], dense=True, style_='width: 300px',
                                                  flat=False)
            self.orders_layout = v.Layout(children=[self.orders_panel], class_='mb-6', dense=True, flat=False)
            self.children = [self.title,
                             'Manipulated Variables (MV)', self.mv_select,
                             'Measured Variables (CV)', self.cv_select,
                             'Method', self.method_select,
                             self.orders_layout,
                             v.Divider(class_='mb-4'),
                             'Training Conditions', self.train_condition,
                             'Validation Conditions', self.validation_condition,
                             v.Divider(class_='mb-6'),
                             self.identify_push_card]

            
            
            
            
            
# Neural Network Panel
class NN_Panel(Left_Panel):
    def __init__(self, *args, **kwargs):
        model_name = 'NeuralNetwork'
        super().__init__(model_name=model_name,
                         *args, **kwargs)

        # Icons
        title_icon = v.Icon(class_='', children=['mdi-tools'], color='white')

        # Mode Switch
        switch_values = ['Manual', 'Auto']
        self.options_switch = v.Switch(tag='switch',
                                       v_model=True,
                                       inset=True,
                                       label='Manual',
                                       dark=False,
                                       vertical=True,
                                       dense=True,
                                       )

        self.options_switch.label = switch_values[self.options_switch.v_model]
        self.options_switch.on_event('change', self.mode_select_action)
        self.mode_row = v.Card(children=['Mode', v.Spacer(), self.options_switch], 
                               color='none',
                               flat=True,
                               class_='d-flex justify-center flex-row align-center pt-1 mx-1',
                               style_='font-size:12pt; font-weight:bold; height:40px',
                               dense=True)
        
        # Auto Mode Widgets
        self.slider_help_tip_btn = v.Btn(icon=True, v_on='help_tooltip.on', children=[v.Icon(children=['mdi-help-circle-outline'])])
        self.slider_help_tip = v.Tooltip(bottom=True,
                                         max_width='290px',
                                         v_slots=[{'name': 'activator',
                                                                'variable': 'help_tooltip',
                                                                'children': self.slider_help_tip_btn
                                                               }], children=['Higher computaional cost requires more time but the accuracy is higher.'])
        
        self.auto_slider_title = v.Row(children=[v.Icon(children=['mdi-brain'], class_='px-2 pb-0 mb-0'),
                                                 'Computation Cost',
                                                 v.Spacer(),
                                                 self.slider_help_tip], 
                                       align='center',
                                       class_='pb-0 pt-1 px-1',
                                       style_='font-size:11pt')
        self.auto_mode_slider = v.Slider(tick_labels=['Low', 'Medium', 'High'], 
                                         max=2,
                                         v_model='0',
                                         style_='font-size:10pt; font-weight:bold',
                                         class_='',
                                         dense=True,
                                         dark=False)
        self.auto_mode_list = [self.auto_slider_title, self.auto_mode_slider]
        
        
        # Manual Mode Widgets (Coming Soon...)
        self.manual_btn_title = v.Row(children=[v.Icon(children=['mdi-graph-outline'], class_='px-2 pb-0 mb-1'), 'Custom Neural Network'], 
                               class_='pb-0 pt-1 px-1',
                               style_='font-size:11pt')
        self.manual_mode_btn = v.Btn(children=['Coming Soon...'], class_='d-flex justify-center my-1', align='center', dark=False, disabled=True)
        self.manual_mode_btn.on_event('click', self.manual_mode_btn_action)
        self.manual_mode_list = [self.manual_btn_title, self.manual_mode_btn]
        
        self.custom_nn_card = v.Card(color='white', children=['Hello World'], height='80%', align='center', class_='d-flex flex-row justify-center')
        self.custom_nn_dialog = v.Dialog(v_model=False,
                                         align='center',
                                         width='50%',
                                         class_='d-flex flex-row justify-center align-center',
                                         align_centered=True,
                                         children=[self.custom_nn_card])
        
        self.custom_nn_dialog.on_event('keydown.stop', lambda *args: None)

        
        
        # Mode Card
        self.mode_card = v.Card(flat=True, class_='d-flex flex-column justify-center py-1', height='80px')
        self.mode_card.children = self.auto_mode_list
        
        self.switch_card = v.Card(children=[self.mode_row,
                                            v.Divider(class_='my-2'),
                                            self.mode_card],                           
                                            color='white', class_='px-3 py-1 mb-4 mt-0')

               

        # Neural Network
        self.title = v.Card(class_='pt-5 mb-7 mx-0 d-flex justify-left', style_='font-size:20px; background:none',
                            dark=True, center=True, align='center', flat=True,
                            children=[title_icon, v.Divider(vertical=True, class_='mx-2'),
                                      '{} Settings'.format('Neural Network')])

        self.children = [self.title,
                         'Manipulated Variables (MV)', self.mv_select,
                         'Measured Variables (CV)', self.cv_select,
                         v.Divider(class_='mb-4'),
                         self.switch_card,
                         self.custom_nn_dialog,
                         v.Divider(class_='mb-4'),
                         'Training Conditions', self.train_condition,
                         'Validation Conditions', self.validation_condition,
                         v.Divider(class_='mb-6'),
                         self.identify_push_card]

    def mode_select_action(self, item, *_):
        switch_values = ['Manual', 'Auto']
        item.v_model != item.v_model
        item.label = switch_values[item.v_model]
        if item.label == 'Manual':
            self.mode_card.children = self.manual_mode_list

        elif item.label == 'Auto':
            self.mode_card.children = self.auto_mode_list
            
    def manual_mode_btn_action(self, *_):
        self.custom_nn_dialog.v_model = True
            
            
            
            
            
            
            
            
            
            
# Try Widgets

# panel_ss = SS_Panel()
# panel_arx = Arx_Panel()
# panel_arx
# panel_ss
