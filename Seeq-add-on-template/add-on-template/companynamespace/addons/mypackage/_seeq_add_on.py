import warnings
import ipyvuetify as v
import ipywidgets as widgets
import pandas as pd
import plotly.graph_objects as go
from IPython.display import HTML, clear_output, display

from . import create_new_signal, df_plot, pull_only_signals
from ._backend import get_workbook_worksheet_workstep_ids, get_worksheet_url, push_signal

warnings.filterwarnings('ignore')


class MyAddOn:
    colors = {
        'app_bar': '#007960',
        'controls_background': '#F6F6F6',
        'visualization_background': '#FFFFFF',
        'seeq_primary': '#007960',
    }

    additional_styles = widgets.HTML("""
        <style>
        .background_box { background-color:#007960 !important; } 
        .js-plotly-plot .plotly .modebar-btn[data-title="Produced with Plotly"] {display: none;}
        .vuetify-styles .theme--light.v-list-item .v-list-item__action-text, 
        .vuetify-styles .theme--light.v-list-item .v-list-item__subtitle {color: #212529;}
        .vuetify-styles .theme--light.v-list-item:not(.v-list-item--active):not(.v-list-item--disabled) 
        {color: #007960 !important;}
        .vuetify-styles .v-label {font-size: 14px;}
        .vuetify-styles .v-application {font-family: "Source Sans Pro","Helvetica Neue",Helvetica,Arial,sans-serif;}
        </style>""")
    v.theme.themes.light.success = '#007960'
    v.theme.themes.light.primary = '#007960'
    no_data_message = 'No plot available'

    def __init__(self, sdl_notebook_url):
        self.workbook_id, self.worksheet_id, self.workstep_id = get_workbook_worksheet_workstep_ids(
            sdl_notebook_url)
        self.worksheet_url = get_worksheet_url(sdl_notebook_url)
        self.df = pull_only_signals(self.worksheet_url)
        self.result_signal = pd.DataFrame()
        clear_output()

        self.graph = go.FigureWidget()
        self.create_displayed_fig(df_plot(pd.DataFrame))

        # App layout
        self.hamburger_menu = HamburgerMenu()
        self.app = v.App(v_model=None, id='dummy-addon-app')
        self.appBar = v.AppBar(
            color=self.colors['app_bar'],
            dense=True,
            dark=True,
            children=[v.ToolbarTitle(children=['My Add-On']),
                      v.Spacer(),
                      v.Divider(vertical=True),
                      self.hamburger_menu])

        self.signal_a = create_dropdowns(list(self.df.columns),
                                         label='Select first signal',
                                         color=self.colors['seeq_primary'],
                                         style_='max-width: 500px', class_='mr-5')
        self.signal_b = create_dropdowns(list(self.df.columns),
                                         label='Select second signal',
                                         color=self.colors['seeq_primary'],
                                         style_='max-width: 500px', class_='mr-5')
        self.operator = create_dropdowns(['+', '-', 'x', '/'],
                                         label='Select math operation',
                                         color=self.colors['seeq_primary'],
                                         v_model='+', style_='max-width: 70px', class_='mr-5')

        self.create_signals = v.Btn(color='success', children=['Signal to Workbench'],
                                    target="_blank", disabled=True, loading=False,
                                    class_='', style_='text-transform: capitalize;')

        self.dropdowns_container = v.Html(tag='div', class_='d-flex flex-row flex-wrap pr-3 pt-2',
                                          style_=f"background-color: {self.colors['controls_background']}; opacity: 1",
                                          children=[self.signal_a, self.operator, self.signal_b])

        self.container = v.Html(tag='div', class_='d-flex flex-row flex-wrap justify-space-between pr-3 pt-2',
                                style_=f"background-color: {self.colors['controls_background']}; opacity: 1",
                                children=[self.dropdowns_container, self.create_signals])

        # controls bar
        self.controls = v.Html(tag='div', class_='d-flex flex-column pr-3 pl-3 pt-5',
                               style_=f"background-color: {self.colors['controls_background']}; opacity: 1",
                               children=['Choose signals and math operator', self.container])

        # Visualization container
        self.visualization = v.Html(tag='div', id='plotly-heatmap',
                                    style_=f"background-color: {self.colors['visualization_background']};"
                                           f"border:2px solid {self.colors['controls_background']};",
                                    children=[self.graph])

    def create_displayed_fig(self, fig):
        if fig is None:
            self.graph = self.no_data_message
            return
        self.graph = go.FigureWidget(fig)

    def math_operation(self):
        if self.operator.v_model == '+':
            return 'add'
        if self.operator.v_model == '-':
            return 'subtract'
        if self.operator.v_model == 'x':
            return 'multiply'
        if self.operator.v_model == '/':
            return 'divide'

    def update_display(self, *_):
        self.result_signal = pd.DataFrame()
        self.create_signals.disabled = True
        if {self.signal_a.v_model, self.signal_b.v_model}.issubset(set(self.df.columns)):
            self.result_signal = create_new_signal(self.df[self.signal_a.v_model].values,
                                                   self.df[self.signal_b.v_model].values,
                                                   self.df.index,
                                                   self.math_operation())
            self.create_signals.disabled = False
        fig = df_plot(self.result_signal)
        self.create_displayed_fig(fig)
        self.visualization.children = [self.graph]

    def push_to_seeq(self, *_):
        push_signal(self.result_signal, self.workbook_id, 'From My Add-on')

    def run(self):
        # noinspection PyTypeChecker
        display(HTML("<style>.container { width:100% !important; }</style>"))
        self.app.children = [self.appBar, self.controls, self.visualization, self.additional_styles]
        self.signal_a.on_event('change', self.update_display)
        self.signal_b.on_event('change', self.update_display)
        self.operator.on_event('change', self.update_display)
        self.create_signals.on_event('click', self.push_to_seeq)
        return self.app


class HamburgerMenu(v.Menu):
    def __init__(self, **kwargs):
        self.hamburger_button = v.AppBarNavIcon(v_on='menuData.on')
        self.help_button = v.ListItem(value='help',
                                      ripple=True,
                                      href='mailto: support@company.com?subject=MyAddOn Feedback',
                                      children=[v.ListItemAction(class_='mr-2 ml-0',
                                                                 children=[v.Icon(color='#212529',
                                                                                  children=['fa-life-ring'])]),
                                                v.ListItemActionText(children=[f'Send Support Request'])
                                                ])
        self.items = [v.Divider(), self.help_button, v.Divider()]

        super().__init__(offset_y=True,
                         offset_x=False,
                         left=True,
                         v_slots=[{
                             'name': 'activator',
                             'variable': 'menuData',
                             'children': self.hamburger_button,
                         }]
                         ,
                         children=[
                             v.List(children=self.items)
                         ]
                         , **kwargs)


def create_dropdowns(items: list, label='', color='', v_model='', class_='', style_=''):
    return v.Select(label=label,
                    items=items,
                    dense=True,
                    outlined=True,
                    color=color, filled=True,
                    item_color='primary',
                    v_model=v_model,
                    style_=style_,
                    class_=class_)
