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

# Try Widgets

# panel_ss = SS_Panel()
# panel_arx = Arx_Panel()
# panel_arx
# panel_ss
