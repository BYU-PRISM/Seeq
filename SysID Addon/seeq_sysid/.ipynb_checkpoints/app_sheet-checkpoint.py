from copy import deepcopy

import ipyvuetify as v
from pandas import DataFrame

from seeq_sysid._backend import push_formula
from seeq_sysid.figure_panel import Figure_Table
from seeq_sysid.left_panel import Left_Panel
from seeq_sysid.model_obj import Model_Obj, ARX, Subspace
from seeq_sysid.panels import Arx_Panel, SS_Panel


class App_Sheet(v.Card):
    def __init__(self,
                 panel: Left_Panel,
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
                         *args, **kwargs)

        self.train_results = None
        self.validation_results = None

        self.panel = panel
        self.canvas = Figure_Table()

        self.model_name = panel.model_name
        self.model = Model_Obj()
        self.blank_model = deepcopy(self.model)
        self.addon_worksheet = 'From ' + self.model_name + ' Addon'

        # General Widgets
        self.mv_select = panel.mv_select
        self.cv_select = panel.cv_select

        self.train_condition = panel.train_condition
        self.validation_condition = panel.validation_condition

        self.push_model_btn = panel.push_model_btn
        self.identify_model_btn = panel.identify_model_btn

        self.signal_df = DataFrame()
        self.capsule_df = DataFrame()
        self.tags_df = DataFrame()
        self.workbook_id = workbook_id

        # Actions
        self.mv_select.on_event('change', self.update_panel)
        self.cv_select.on_event('change', self.update_panel)
        self.identify_model_btn.on_event('click', self.identify_system)
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
            self.push_model_btn.disabled = True

    def identify_system(self, *_):
        self.prepare_params_general()
        self.prepare_params_spec()

        train_dataset = self.create_dataset(self.train_condition.v_model)
        validation_dataset = self.create_dataset(self.validation_condition.v_model)

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
        else:
            self.push_model_btn.disabled = True

    def create_dataset(self, capsules: list):
        signal_df = self.signal_df
        capsule_df = self.capsule_df

        if not capsules:
            return signal_df

        return signal_df[capsule_df[capsules].sum(axis=1) == True]

    def push_model(self, *_):
        if self.general_validation():
            return None

        self.model.create_formula(self.tags_df)

        push_formula(self.model.formula, self.workbook_id, self.addon_worksheet)

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


class Arx_app_sheet(App_Sheet):
    def __init__(self,
                 *args, **kwargs):
        panel = Arx_Panel()
        super().__init__(panel=panel,
                         *args, **kwargs)
        self.model = ARX()
        self.blank_model = deepcopy(self.model)

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


class SS_app_sheet(App_Sheet):
    def __init__(self,
                 *args, **kwargs):
        panel = SS_Panel()
        super().__init__(panel=panel,
                         *args, **kwargs)
        self.model = Subspace()
        self.blank_model = deepcopy(self.model)

        self.method = self.panel.method_select
        self.thresh = self.panel.threshold_box
        self.order = self.panel.order_box

    def prepare_params_spec(self):
        self.model.method = self.method.v_model
        self.model.thresh = float(self.thresh.v_model)
        self.model.order = int(self.order.v_model)