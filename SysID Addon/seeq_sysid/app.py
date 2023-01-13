import ipyvuetify as v
import ipywidgets as widgets
from pandas import DataFrame
# from pandas import read_csv, read_excel # For Local Run

from seeq_sysid.gui.panels import ARXPanel, SSPanel, NNPanel

from seeq_sysid.gui.app_sheet import AppSheet, ARXAppSheet, SSAppSheet, NNAppSheet, TFAppSheet
from seeq_sysid.gui.app_bar import AppBar

from seeq_sysid.gui._backend import *
import urllib.parse as urlparse
from urllib.parse import parse_qs
from seeq import spy

import warnings
warnings.filterwarnings('ignore')

from IPython.display import HTML, clear_output, display, Javascript


class SYSID:

    colors = {
        'app_bar': '#007960',
        'controls_background': '#F6F6F6',
        'visualization_background': '#FFFFFF',
        'seeq_primary': '#007960',
    }

    additional_styles = widgets.HTML("""
        <style>
	   #appmode-leave {display: none;}
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
    
    def __init__(self, sdl_notebook_url=''):
        self.worksheet_url = ''
    
        # Server Mode
        self.addon_worksheet = 'From SysID AddOn'
        self.workbook_id = None
        self.worksheet_url = None
        
        try:
            sdl_notebook_url = sdl_notebook_url
            self.workbook_id, self.worksheet_id, self.workstep_id = get_workbook_worksheet_workstep_ids(sdl_notebook_url)
            self.worksheet_url = get_worksheet_url(sdl_notebook_url)
            self.signal_df, self.capsule_df, self.tags_df = pull_signals(self.worksheet_url)

        except:
            self.signal_df = DataFrame()
            self.capsule_df = DataFrame()
            self.tags_df = DataFrame()
        
        # Local Mode
        # self.signal_df = read_csv('data/TE_signal_lite.csv', index_col='Time')
        # self.capsule_df = read_csv('data/TE_capsules_lite.csv', index_col='Time')
        
        # self.signal_df = read_csv('data/DEB.csv', index_col='Time')
        # self.capsule_df = read_csv('data/DEB capsules.csv', index_col='Time')
        
        # self.signal_df = read_csv('data/signal_df.csv', index_col='Time')
        # self.capsule_df = read_csv('data/capsule_df.csv', index_col='Time')
        
        self.app = v.App(class_='ma-2')
        
        
        self.arx_sheet = ARXAppSheet()
        self.arx_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)

        self.ss_sheet = SSAppSheet()
        self.ss_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)

        self.nn_sheet = NNAppSheet()
        self.nn_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)
        
        self.tf_sheet = TFAppSheet() 
        self.tf_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)

    
        self.arx_tab = v.Tab(children=['Time Series'], 
                        style_='font-weight:bold; font-size:12pt')
        
        self.ss_tab = v.Tab(children=['Subspace'], 
                       style_='font-weight:bold; font-size:12pt')
        
        self.nn_tab = v.Tab(children=['Neural Network'], 
                       style_='font-weight:bold; font-size:12pt')
        
        self.tf_tab = v.Tab(children=['Transfer Function'], 
                       style_='font-weight:bold; font-size:12pt')

        self.tabs = [self.arx_tab, self.ss_tab, self.nn_tab, self.tf_tab]
        

        self.arx_tab_item = v.TabItem(children=[self.arx_sheet], 
                                 class_='',
                                 transition='none', 
                                 reverse_transition='none')

        self.ss_tab_items = v.TabItem(children=[self.ss_sheet],
                                 class_='',
                                 transition='none',
                                 reverse_transition='none')
        
        self.nn_tab_items = v.TabItem(children=[self.nn_sheet],
                         class_='',
                         transition='none',
                         reverse_transition='none')
        
        self.tf_tab_items = v.TabItem(children=[self.tf_sheet],
                        class_='',
                        transition='none',
                        reverse_transition='none')

        items = [self.arx_tab_item, self.ss_tab_items, self.nn_tab_items, self.tf_tab_items]

        self.app_bar = AppBar(self.tabs, items)
        
        self.worksheet_url_box = self.app_bar.ham_menu.worksheet_url
        self.ok_url_dialog_btn = self.app_bar.ham_menu.ok_url_dialog_btn
        self.close_url_dialog_btn = self.app_bar.ham_menu.close_url_dialog_btn
        
        self.ok_url_dialog_btn.on_event('click',self.ok_url_action)
        self.close_url_dialog_btn.on_event('click',self.close_url_action)
        
        self.app_bar.ham_menu.load_data_editor.on_event('click', self.load_data_editor_action)
        self.done_data_editor_btn = self.app_bar.ham_menu.data_editor.done_btn
        self.done_data_editor_btn.on_event('click', self.done_data_editor_action)


    def run(self):
        clear_output()
        display(HTML("""<style>.container {width:100% !important}</style>"""))
        self.app.children = [self.app_bar, SYSID.additional_styles]
        return self.app
    
    
    def load_worksheet(self):
        worksheet_url = self.worksheet_url_box.v_model
        if not self.app_bar.ham_menu.sl_switch.v_model:
            if worksheet_url:
                sdl_notebook_url = f'{spy.utils.get_data_lab_project_url()}/dummy.ipynb?workbookId={spy.utils.get_workbook_id_from_url(worksheet_url)}&worksheetId={spy.utils.get_worksheet_id_from_url(worksheet_url)}'
                self.workbook_id, self.worksheet_id, self.workstep_id = get_workbook_worksheet_workstep_ids(sdl_notebook_url)
                self.worksheet_url = get_worksheet_url(sdl_notebook_url)
                self.signal_df, self.capsule_df, self.tags_df = pull_signals(self.worksheet_url)
        else:
            self.signal_df = self.app_bar.ham_menu.local_data
         
        
        self.arx_sheet = ARXAppSheet()
        self.arx_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)

        self.ss_sheet = SSAppSheet()
        self.ss_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)

        self.nn_sheet = NNAppSheet()
        self.nn_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)
        
        self.tf_sheet = TFAppSheet()
        self.tf_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)

        
        self.arx_tab_item = v.TabItem(children=[self.arx_sheet], 
                                 class_='',
                                 transition='none', 
                                 reverse_transition='none')

        self.ss_tab_items = v.TabItem(children=[self.ss_sheet],
                                 class_='',
                                 transition='none',
                                 reverse_transition='none')
        
        self.nn_tab_items = v.TabItem(children=[self.nn_sheet],
                         class_='',
                         transition='none',
                         reverse_transition='none')
        
        self.tf_tab_items = v.TabItem(children=[self.tf_sheet],
                    class_='',
                    transition='none',
                    reverse_transition='none')

        items = [self.arx_tab_item, self.ss_tab_items, self.nn_tab_items, self.tf_tab_items]

        self.app_bar = AppBar(self.tabs, items)

        self.worksheet_url_box = self.app_bar.ham_menu.worksheet_url
        self.ok_url_dialog_btn = self.app_bar.ham_menu.ok_url_dialog_btn
        self.close_url_dialog_btn = self.app_bar.ham_menu.close_url_dialog_btn
        
        self.ok_url_dialog_btn.on_event('click',self.ok_url_action)
        self.close_url_dialog_btn.on_event('click',self.close_url_action)
        
        self.app_bar.ham_menu.load_data_editor.on_event('click', self.load_data_editor_action)
        self.done_data_editor_btn = self.app_bar.ham_menu.data_editor.done_btn
        self.done_data_editor_btn.on_event('click', self.done_data_editor_action)

        clear_output()
        display(HTML("""<style>.container {width:100% !important}</style>"""))
        self.app.children = [self.app_bar, SYSID.additional_styles]
        display(self.app)            

    def close_url_action(self, *args):
        self.worksheet_url_box.v_model = self.worksheet_url
        self.app_bar.ham_menu.url_dialog.v_model = None

    def ok_url_action(self, *args):
        self.ok_url_dialog_btn.loading = True
        self.worksheet_url = self.worksheet_url_box.v_model
        self.load_worksheet()
        self.worksheet_url_box.v_model = self.worksheet_url
        self.ok_url_dialog_btn.loading = False
        self.app_bar.ham_menu.url_dialog.v_model = None
        
    # DataEditor event functions (Post)
    def load_data_editor_action(self, *args):
        self.app_bar.ham_menu.data_editor.set_data(self.signal_df)
        self.app_bar.ham_menu.data_editor_dialog.v_model = True
        self.app_bar.ham_menu.data_editor.update_figure(self.signal_df)
        
    def done_data_editor_action(self, *args):
        self.done_data_editor_btn.loading = True
        self.signal_df = self.app_bar.ham_menu.data_editor.df.copy()
        if not self.capsule_df.empty:
            self.capsule_df = self.capsule_df.loc[self.signal_df.index]
        self.arx_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)
        self.ss_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)
        self.nn_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)
        self.tf_sheet.set_data(self.signal_df, self.capsule_df, self.tags_df, self.workbook_id)
        self.done_data_editor_btn.loading = False
        self.app_bar.ham_menu.data_editor_dialog.v_model = None