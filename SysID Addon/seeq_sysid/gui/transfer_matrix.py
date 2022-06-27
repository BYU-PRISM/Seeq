import ipyvuetify as v

from plotly.express.colors import qualitative

from seeq_sysid.gui.transfer_chip import TransferChip
from seeq_sysid.model.tf_item import TransferItem, TransferOption
from seeq_sysid.model.tf import TF

from pandas import DataFrame, concat


class TransferMatrix(v.Card):
    def __init__(self,
                 df=DataFrame(),
                 
                 elevation=0,
                 **kwargs):
        super().__init__(elevation=elevation,
                         style_='width:100%; overflow:auto auto',
                         **kwargs)
        self.mv = None
        self.cv = None
        self.matrix_dic = {}
        self.cv_label_dict = {}
        self.card_colors = qualitative.Plotly
        self.df = df.copy()
        self.model = None
        
        self.temp_df = None
        self.train_df = DataFrame()
        self.validation_df = DataFrame()
        
        self.signal_df = None
        self.capsules_df = None
        
        TransferChip.reset()

    def create_matrix(self, signal_df=DataFrame(), capsule_df=DataFrame(), mv=[], cv=[], train_capsules=[], valid_capsules=[]):
        self.signal_df = signal_df.copy()
        self.capsule_df = capsule_df.copy()
        self.mv = mv
        self.cv = cv
        matrix_list = []
        header_list = []
        row_list = []
        rows_list = []
        n_cv = 0
        n_mv = len(self.mv)
        
        # Create Header
        blank_block = v.Card(children=[''], class_='d-flex flex-column ma-1 pa-0 justify-center align-center', style_='width:170px; height:40px; font-weight:bold; font-size:10pt')
        header_list.append(blank_block)
        for mv_i in self.mv:
            header_list.append(v.Card(children=[mv_i], class_='d-flex flex-row ma-1 pa-0 justify-center align-center', style_='width:168px; height:40px; font-weight:bold; font-size:10pt'))
        
        blank_block1 = v.Card(children=[''], class_='d-flex flex-column ma-1 pa-0 justify-center align-center', elevation=0, style_='width:170px; height:40px; font-weight:bold; font-size:10pt')
        mv_label = [v.Card(children=[blank_block1, v.Card(children=['MV'], class_='d-flex flex-column ma-1 mb-0 pa-0 justify-center align-center', 
                                                        style_='width:{}px; height:40px; font-weight:bold; font-size:10pt'.format(174*n_mv))], 
                          class_='d-flex justify-left align-left ma-1 pa-0',
                          style_='font-weight:bold; font-size:10pt',
                          elevation=0)]
        
        matrix_list.append(v.Card(children=mv_label, style_='', class_='d-flex justify-left align-left flex-row ma-1 pa-0 ml-0 mb-0', elevation=0))
        matrix_list.append(v.Card(children=header_list, style_='', class_='d-flex justify-left flex-row ma-1 mt-0', elevation=0))

        
        for cv_i in self.cv:
            cv_label = CVLabel(cv_i=cv_i, v_on = cv_i+'capsulemenu.on')

            self.cv_label_dict[cv_i] = CapsulesCard(items=capsule_df.columns.to_list(), selected_train_conditions=train_capsules, selected_valid_conditions=valid_capsules)
            capsules_menu = v.Menu(value=None, children=[self.cv_label_dict[cv_i]], class_='ma-2 pa-2', close_on_content_click=False, v_slots=[{
                             'name': 'activator',
                             'variable': cv_i+'capsulemenu',
                             'children': [cv_label]
                         }],)
            
            
            self.matrix_dic[cv_i] = {}
            row_list = [cv_label, capsules_menu]

            for mv_i in self.mv:
                self.matrix_dic[cv_i][mv_i] = TransferChip(mv_i, cv_i)
                self.matrix_dic[cv_i][mv_i].update_meas_figure(self.signal_df)
            
            row_list.extend(list(self.matrix_dic[cv_i].values()))
            matrix_list.append(v.Card(children=row_list, style_='', class_='d-flex justify-left flex-row ma-1', elevation=0))
            
            n_cv += 1
        
        self.children = matrix_list
    
    def run(self, *args):
        self.to_identify()
        
    def compile_matrix(self):
        for cv_i in self.cv:
            for mv_i in self.mv:
                self.matrix_dic[cv_i][mv_i].compile_item()
                
    def create_model(self):
        self.model = TF()
        self.model.cv = []
        
        self.compile_matrix()

        for cv_i in self.cv:            
            transfer_item = TransferItem()
            transfer_item.cv = [cv_i]
            
            TransferOption.reset_idx()

            for mv_i in self.mv:
                item: TransferChip = self.matrix_dic[cv_i][mv_i]
                if item.tf_card_btn.value:
                    item.tf_card_btn.children = [item.loading_settings]
                item.tf_card_btn.disabled = True
                
                if self.matrix_dic[cv_i][mv_i].tf_card_btn.value:    
                    order = item.order
                    no_gain = item.no_gain
                    no_ramp = item.no_ramp
                    is_dt = item.is_dt
                    
                    gain_lb = item.gain_lb
                    gain_ub = item.gain_ub
                    
                    tau_lb = item.tau_lb
                    tau_ub = item.tau_ub
                    
                    deadtime_lb = item.deadtime_lb
                    deadtime_ub = item.deadtime_ub
                    
                    tf_option = TransferOption(order=order,
                                               no_gain=no_gain,
                                               no_ramp=no_ramp,
                                               is_dt=is_dt,
                                               gain_lb=gain_lb,
                                               gain_ub=gain_ub,
                                               tau_lb=tau_lb,
                                               tau_ub=tau_ub,
                                               theta_lb=deadtime_lb,
                                               theta_ub=deadtime_ub,
                                               name=mv_i)
                    
                    tf_option.id = TransferOption.idx
                    transfer_item.option_dict[mv_i] = tf_option
                    TransferOption.add_idx()
                
            if TransferOption.idx:
                self.model.add_model(cv_i, transfer_item)
    
    
    def create_dataset(self, capsules: list = None):
        signal_df = self.signal_df.copy()
        capsule_df = self.capsule_df.copy()

        if not capsules:
            return signal_df

        return signal_df[capsule_df[capsules].sum(axis=1) == True]
    
    
    def to_identify(self):
        signal_df = self.signal_df.copy()
        self.create_model()
        
        self.train_df = DataFrame()
        
        for cv_i in self.model.cv:
            # try:
            capsules = self.cv_label_dict[cv_i].select_train_capsules.v_model
            train_df = self.create_dataset(capsules)
            y_train_df = self.model.identify(train_df, cv_i)

            self.train_df = concat([self.train_df, y_train_df], axis=1)
            self.to_step_response(cv_i)

            self.train_df = concat([self.train_df, train_df[cv_i]], axis=1)
            # except:
                # pass
        
            
            
    def to_step_response(self, cv_name):
        for mv_i in self.mv:
            chip = self.matrix_dic[cv_name][mv_i]
        
            if chip.tf_card_btn.value:
                try:
                    ys_df = self.model.step_response(mv_name=mv_i, cv_name=cv_name)
                    self.temp_df = ys_df
                    chip.order, chip.gain_gui, chip.tau_gui, chip.theta_gui, chip.zeta_gui = self.model.get_model_info(mv_name=mv_i, cv_name=cv_name)
                    chip.ts, chip.tr, chip.os = self.model.get_step_info(mv_name=mv_i, cv_name=cv_name)
                    chip.update_result_dialog(df=ys_df)     
                    chip.switch_chip()
                except:
                    chip.switch_chip()
                    chip.children = [chip.no_solution_card]
            
            else:
                chip.disabled = True
                
    def to_validation(self):
        self.validation_df = DataFrame()

        for cv_i in self.model.cv:
            capsules = self.cv_label_dict[cv_i].select_validation_capsules.v_model
            validation_df = self.create_dataset(capsules)
            self.temp_df = validation_df
            yp_valid_df = self.model.predict(validation_df, cv_i)

            self.validation_df = concat([self.validation_df, yp_valid_df], axis=1)
            self.validation_df = concat([self.validation_df, validation_df[cv_i]], axis=1)  
                    

class CapsulesCard(v.Card):
    def __init__(self,
                 items=[],
                 selected_train_conditions=[],
                 selected_valid_conditions=[],
                 class_='d-flex flex-column ma-0 pa-0 pl-5 pt-5 justify-start',
                 style_='width:320px; height:200px; font-weight:bold; font-size:10pt',
                 outlined=False):
        super().__init__(class_=class_, 
                         style_=style_,
                         outlined=outlined)

        self.select_train_capsules = v.Select(tag='Training Condition',
                                        v_model=selected_train_conditions,
                                        items=items,
                                        color='success',
                                        item_color='success',
                                        dense=True,
                                        outlined=False,
                                        class_='d-flex justify-start align-start ma-0 pa-0 mt-2 mb-2',
                                        style_='width: 95%; font-size:12px',
                                        filled=True,
                                        background_color='#EDF4FF',
                                        placeholder='Select',
                                        multiple=True,
                                        hide_details=True,
                                        clearable=True,
                                        solo=True)
        
        self.select_validation_capsules = v.Select(tag='Validation Condition',
                                                   v_model=selected_valid_conditions,
                                                   items=items,
                                                   color='success',
                                                   item_color='success',
                                                   dense=True,
                                                   outlined=False,
                                                   class_='d-flex justify-start align-start ma-0 pa-0 mt-2',
                                                   style_='width: 95%; font-size:12px',
                                                   filled=True,
                                                   background_color='#EDF4FF',
                                                   placeholder='Select',
                                                   multiple=True,
                                                   hide_details=True,
                                                   clearable=True,
                                                   solo=True)
            
        self.children=['Training Condition', self.select_train_capsules,
                       'Validation Condition', self.select_validation_capsules]

        
class CVLabel(v.Btn):
    def __init__(self,
                 cv_i='',
                 items=[],
                 class_='d-flex flex-column ma-1 pa-0 justify-center align-center',
                 style_='width:170px; height:95px; font-weight:bold; font-size:10pt',
                 outlined=False,
                 color='white',
                 *args, **kwargs):
        super().__init__(class_=class_, 
                         style_=style_,
                         outlined=outlined,
                         color=color,
                         *args, **kwargs)
        self.children = [cv_i]