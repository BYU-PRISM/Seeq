from copy import deepcopy

import ipyvuetify as v
from pandas import DataFrame, to_datetime

from ._backend import push_formula, push_signal

from .figure_table import FigureTable
from .panels import LeftPanel, ARXPanel, SSPanel, NNPanel

from seeq_sysid.model.base import Model
from seeq_sysid.model.arx import ARX
from seeq_sysid.model.ss import Subspace
from seeq_sysid.model.nn import NN

from .setup import Setup
from .app_bar import AppBar
from .transfer_matrix import TransferMatrix


class AppSheet(v.Card):
    def __init__(self,
                 panel: LeftPanel,
                 workbook_id='',
                 *args, **kwargs):
        class_ = 'd-flex justify-space-between ma-2 pa-2 pt-2 mt-0'
        style_ = 'height:900px; border-radius:12px'
        color = 'white'
        flat = True
        super().__init__(class_=class_,
                         style_=style_,
                         color=color,
                         flat=flat,
                         elevation=0,
                         **kwargs)

        self.train_results = None
        self.validation_results = None
        self.all_results = None

        self.panel = panel
        self.canvas = FigureTable()

        self.model_name = panel.model_name
        self.model = Model()
        self.blank_model = deepcopy(self.model)
        self.addon_worksheet = 'From ' + self.model_name + ' Addon'

        # General Widgets
        self.mv_select = panel.mv_select
        self.cv_select = panel.cv_select

        self.train_condition = panel.train_condition
        self.validation_condition = panel.validation_condition

        self.push_model_btn = panel.push_model_btn
        self.identify_model_btn = panel.identify_model_btn
        self.validate_model_btn = panel.validate_model_btn

        self.signal_df = DataFrame()
        self.capsule_df = DataFrame()
        self.tags_df = DataFrame()
        self.workbook_id = workbook_id

        # Actions
        self.mv_select.on_event('change', self.update_panel)
        self.cv_select.on_event('change', self.update_panel)
        self.identify_model_btn.on_event('click', self.identify_system)
        self.validate_model_btn.on_event('click', self.validate_model)
        self.push_model_btn.on_event('click', self.push_model)

        self.children = [self.panel, self.canvas]

    # Functions
    def set_data(self, signal_df: DataFrame = DataFrame(), capsule_df: DataFrame = DataFrame(), tags_df=DataFrame(),
                 workbook_id: str = ''):
        self.mv_select.items = signal_df.columns.to_list()
        self.cv_select.items = signal_df.columns.to_list()

        self.train_condition.items = capsule_df.columns.to_list()
        self.validation_condition.items = capsule_df.columns.to_list()

        self.signal_df = signal_df
        self.capsule_df = capsule_df
        self.tags_df = tags_df
        self.workbook_id = workbook_id

    def update_panel(self, *_):
        self.mv_select.items = [item for item in self.signal_df.columns if item not in self.cv_select.v_model]
        self.cv_select.items = [item for item in self.signal_df.columns if item not in self.mv_select.v_model]

        if len(self.mv_select.v_model) > 0 and len(self.cv_select.v_model) > 0:
            self.identify_model_btn.disabled = False

        else:
            self.identify_model_btn.disabled = True
            self.validate_model_btn.disabled = True
            self.push_model_btn.disabled = True

    def identify_system(self, *_):
        self.identify_model_btn.loading = True
        self.prepare_params_general()
        self.prepare_params_spec()

        train_dataset = self.create_dataset(self.train_condition.v_model)
        validation_dataset = self.create_dataset(self.validation_condition.v_model)

        self.preprocess()

        self.model.identify(train_dataset)

        self.train_results = self.model.forecast(train_dataset)
        self.train_results.set_index(train_dataset.index, inplace=True)
        self.train_results[self.model.cv] = train_dataset[self.model.cv]

        self.validation_results = self.model.forecast(validation_dataset)
        self.validation_results.set_index(validation_dataset.index, inplace=True)
        self.validation_results[self.model.cv] = validation_dataset[self.model.cv]

        self.canvas.create(self.train_results, self.validation_results)

        if self.model.status:
            self.push_model_btn.disabled = False
            self.validate_model_btn.disabled = False
        else:
            self.push_model_btn.disabled = True
            self.validate_model_btn.disabled = True

        self.identify_model_btn.loading = False

    def create_dataset(self, capsules: list = None):
        signal_df = self.signal_df[self.mv_select.v_model + self.cv_select.v_model]
        capsule_df = self.capsule_df

        if not capsules:
            return signal_df

        return signal_df[capsule_df[capsules].sum(axis=1) == True]

    def validate_model(self, *_):
        self.validate_model_btn.loading = True
        validation_dataset = self.create_dataset(self.validation_condition.v_model)
        self.validation_results = self.model.forecast(validation_dataset)
        self.validation_results.set_index(validation_dataset.index, inplace=True)
        self.validation_results[self.model.cv] = validation_dataset[self.model.cv]

        self.canvas.create(self.train_results, self.validation_results)
        self.validate_model_btn.loading = False

    def push_model(self, *_):
        self.push_model_btn.loading = True

        if self.general_validation():
            return None

        self.model.create_formula(self.tags_df)
        # Measured Data
        signal_df = self.signal_df[self.model.cv]
        push_formula(signal_df, self.model.formula, self.workbook_id, self.addon_worksheet)
        self.push_model_btn.loading = False

    def push_data(self, *_):
        self.push_model_btn.loading = True
        signal_df = self.create_dataset()
        self.all_results = self.model.forecast(signal_df)
        self.all_results.set_index(signal_df.index, inplace=True)
        # self.all_results[self.model.cv] = signal_df[self.model.cv]
        for cv_i in self.model.cv:
            self.all_results[cv_i + ' original'] = signal_df[cv_i]

        push_signal(self.all_results, self.workbook_id, self.addon_worksheet)
        self.push_model_btn.loading = False

    def general_validation(self):
        return 0

    def customized_validation(self):
        return 0

    def prepare_params_general(self):
        self.model = deepcopy(self.blank_model)

        self.model.mv = self.mv_select.v_model
        self.model.cv = self.cv_select.v_model

    def prepare_params_spec(self):
        pass

    def preprocess(self):
        pass


class ARXAppSheet(AppSheet):
    def __init__(self,
                 *args, **kwargs):
        panel = ARXPanel()
        super().__init__(panel=panel,
                         *args, **kwargs)
        self.model = ARX()
        self.blank_model = deepcopy(self.model)

        self.model_struct = self.panel.model_struct_select

        self.na_min = self.panel.na_min
        self.na_max = self.panel.na_max

        self.nb_min = self.panel.nb_min
        self.nb_max = self.panel.nb_max

        self.nk_min = self.panel.nk_min
        self.nk_max = self.panel.nk_max

    def prepare_params_spec(self):
        self.model.na_min = int(self.na_min.v_model)
        self.model.na_max = int(self.na_max.v_model)

        self.model.nb_min = int(self.nb_min.v_model)
        self.model.nb_max = int(self.nb_max.v_model)

        self.model.nk_min = int(self.nk_min.v_model)
        self.model.nk_max = int(self.nk_max.v_model)

        self.model.model_struct = self.model_struct.v_model


class SSAppSheet(AppSheet):
    def __init__(self,
                 *args, **kwargs):
        panel = SSPanel()
        super().__init__(panel=panel,
                         *args, **kwargs)
        self.model = Subspace()
        self.blank_model = deepcopy(self.model)

        self.method = self.panel.method_select
        self.thresh = self.panel.threshold_box
        self.order = self.panel.order_box
        self.multiplier_min = self.panel.multiplier_min
        self.multiplier_max = self.panel.multiplier_max
        self.shift_type = self.panel.shift_type

        self.push_model_btn.on_event('click', self.push_data)

    def prepare_params_spec(self):
        self.model.method = self.method.v_model
        self.model.thresh = float(self.thresh.v_model)
        self.model.order = int(self.order.v_model)
        self.model.om_min = int(self.multiplier_min.v_model)
        self.model.om_max = int(self.multiplier_max.v_model)
        self.model.shift_type = self.shift_type.v_model


class NNAppSheet(AppSheet):
    def __init__(self,
                 *args, **kwargs):
        panel = NNPanel()
        super().__init__(panel=panel,
                         *args, **kwargs)
        self.model = NN()
        self.blank_model = deepcopy(self.model)

        self.model.mode = int(self.panel.auto_mode_slider.v_model)

        self.push_model_btn.on_event('click', self.push_data)

    def prepare_params_spec(self):
        self.model.mode = int(self.panel.auto_mode_slider.v_model)

    def preprocess(self):
        self.model.Min = self.signal_df[self.model.mv + self.model.cv].min()
        self.model.Max = self.signal_df[self.model.mv + self.model.cv].max()


class TFAppSheet(v.Card):
    def __init__(self):
        class_ = "d-flex justify-center flex-column mx-auto"
        style_ = 'width:100%; height:850px; border-radius:12px'
        super().__init__(class_=class_,
                         style_=style_,
                         flat=True,
                         elevation=0)

        self.worksheet_url = ''

        # Server Mode
        self.addon_worksheet = 'From TF AddOn'
        self.workbook_id = None
        self.worksheet_url = None
        
        self.signal_df = None
        self.capsule_df = None
        self.tags_df = None

        self.all_results = None

        self.window = v.Window(v_model=0, class_='mt-3', style_='height:100%')

        # Import Sheet
        self.import_sheet = Setup()
        # self.import_sheet.set_data(self.signal_df.columns.to_list(), self.capsule_df.columns.to_list())
        self.import_window = v.WindowItem(children=[self.import_sheet], style_='width:100%', transition='none',
                                          reverse_transition='none')

        # Matrix Sheet x2
        self.matrix_sheet = TransferMatrix()
        self.matrix_window = v.WindowItem(children=[self.matrix_sheet], style_='width:100%', transition='none',
                                          reverse_transition='none')

        # Visualization Sheet
        self.visual_sheet = FigureTable(style_='width:100%; height:780px')
        self.visual_window = v.WindowItem(children=[v.Card(children=[self.visual_sheet])], style_='width:98%',
                                          transition='none', reverse_transition='none')

        # Set Windows
        self.window.children = [self.import_window, self.matrix_window, self.matrix_window, self.visual_window]

        self.app_bar = AppBar(title_list=['Import Data', 'Model Setup', 'Step Response', 'Visualization'])

        self.app_bar.title.children = [self.app_bar.title_list[self.window.v_model]]

        self.app_bar.tabs.children = [self.app_bar.back_btn, v.Spacer(), self.app_bar.title, v.Spacer(),
                                      self.app_bar.next_btn]

        self.worksheet_url_box = self.app_bar.ham_menu.worksheet_url
        self.ok_url_dialog_btn = self.app_bar.ham_menu.ok_url_dialog_btn
        self.close_url_dialog_btn = self.app_bar.ham_menu.close_url_dialog_btn

        self.ok_url_dialog_btn.on_event('click', self.ok_url_action)
        self.close_url_dialog_btn.on_event('click', self.close_url_action)

        self.children = [self.window, self.app_bar]

        # Actions
        self.import_sheet.mv_select.on_event('change', self.update_panel)
        self.import_sheet.cv_select.on_event('change', self.update_panel)
        self.app_bar.back_btn.on_event('click', self.back_button_action)
        self.app_bar.push_btn.on_event('click', self.push_model)

        self.update_nav()
        self.update_panel()

    def update_nav(self):
        page_num = self.window.v_model

        self.app_bar.title.children = [self.app_bar.title_list[self.window.v_model]]

        if page_num == 0:
            self.app_bar.back_btn.disabled = True
            self.app_bar.next_btn.on_event('click', self.import_sheet_next_action)
            self.app_bar.next_btn.children = ['Next >']
            self.app_bar.tabs.children = [self.app_bar.back_btn, v.Spacer(), self.app_bar.title, v.Spacer(),
                                          self.app_bar.next_btn]

        elif page_num == len(self.app_bar.title_list) - 1:
            self.app_bar.tabs.children = [self.app_bar.back_btn, v.Spacer(), self.app_bar.title, v.Spacer(),
                                          self.app_bar.push_btn]

        elif page_num == 2:
            self.app_bar.back_btn.disabled = False
            self.app_bar.tabs.children = [self.app_bar.back_btn, v.Spacer(), self.app_bar.title, v.Spacer(),
                                          self.app_bar.next_btn]
            self.app_bar.next_btn.on_event('click', self.step_sheet_next_action)

        elif page_num == 1:
            self.app_bar.back_btn.disabled = False
            self.app_bar.next_btn.on_event('click', self.matrix_sheet_next_action)
            self.app_bar.tabs.children = [self.app_bar.back_btn, v.Spacer(), self.app_bar.title, v.Spacer(),
                                          self.app_bar.next_btn]

    def update_panel(self, *_):
        mv_select = self.import_sheet.mv_select
        cv_select = self.import_sheet.cv_select

        mv_select.items = [item for item in self.import_sheet.signal if item not in cv_select.v_model]
        cv_select.items = [item for item in self.import_sheet.signal if item not in mv_select.v_model]

        if len(mv_select.v_model) > 0 and len(cv_select.v_model) > 0:
            self.app_bar.next_btn.disabled = False

        else:
            self.app_bar.next_btn.disabled = True

    def import_sheet_next_action(self, item, *args):
        mv, cv = self.import_sheet.get_data()

        item.loading = True
        self.matrix_sheet = TransferMatrix()
        self.matrix_sheet.create_matrix(signal_df=self.signal_df[mv + cv], capsule_df=self.capsule_df,
                                        mv=mv, cv=cv,
                                        train_capsules=self.import_sheet.train_condition_select.v_model,
                                        valid_capsules=self.import_sheet.valid_condition_select.v_model)
        self.matrix_window.children = [self.matrix_sheet]
        self.window.children = [self.import_window, self.matrix_window, self.matrix_window, self.visual_window]

        item.loading = False
        self.window.v_model = 1
        self.update_nav()

    def matrix_sheet_next_action(self, item, *args):
        item.loading = True

        self.matrix_sheet.run()

        item.loading = False
        self.window.v_model = 2
        self.update_nav()

    def step_sheet_next_action(self, item, *args):
        item.loading = True

        self.matrix_sheet.to_validation()
        self.visual_sheet = FigureTable(style_='width:100%; height:780px')
        self.visual_sheet.create(self.matrix_sheet.train_df, self.matrix_sheet.validation_df)

        self.window.v_model = 3
        self.update_nav()

        self.visual_window.children = [self.visual_sheet]

        item.loading = False

    def back_button_action(self, *args):
        self.window.v_model += -1
        self.update_nav()

    def run(self):
        clear_output()
        display(HTML("""<style>.container {width:100% !important}</style>"""))
        return self

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

    def push_data(self, *_):
        self.app_bar.push_btn.loading = True

        self.all_results = self.matrix_sheet.validation_df.copy()
        for cv_i in self.matrix_sheet.model.cv:
            self.all_results.rename(columns={cv_i: cv_i + ' original'}, inplace=True)

        self.all_results.index = to_datetime(self.all_results.index)
        push_signal(self.all_results, self.workbook_id, self.addon_worksheet)
        
        self.app_bar.push_btn.loading = False

    def set_data(self, signal_df: DataFrame = DataFrame(), capsule_df: DataFrame = DataFrame(), tags_df=DataFrame(),
                 workbook_id: str = ''):

        self.signal_df = signal_df
        self.capsule_df = capsule_df
        self.tags_df = tags_df
        self.workbook_id = workbook_id

        # Set Imported Data
        self.import_sheet.set_data(self.signal_df.columns.to_list(), self.capsule_df.columns.to_list())
        
    def push_model(self, *_):
        self.app_bar.push_btn.loading = True

        df = self.signal_df.copy()
        self.matrix_sheet.model.create_formula(df, self.tags_df)
        # Measured Data
        signal_df = self.signal_df[self.matrix_sheet.model.cv]
        push_formula(signal_df, self.matrix_sheet.model.formula, self.workbook_id, self.addon_worksheet)
        self.app_bar.push_btn.loading = False
