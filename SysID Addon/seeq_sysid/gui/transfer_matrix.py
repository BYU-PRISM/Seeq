import ipyvuetify as v

from plotly.express.colors import qualitative

from seeq_sysid.gui.transfer_chip import TransferChip
from seeq_sysid.model.tf_item import TransferItem, TransferOption
from seeq_sysid.model.tf import TF

from pandas import DataFrame


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
        self.card_colors = qualitative.Plotly
        self.df = df.copy()
        self.model = None
        
        self.temp_df = None
        self.train_df = DataFrame()
        self.validation_df = DataFrame()
        
        TransferChip.reset()

    def create_matrix(self, df=DataFrame(), mv=[], cv=[]):
        self.df = df.copy()
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
            self.matrix_dic[cv_i] = {}
            row_list = [v.Card(children=[cv_i], 
                               class_='d-flex flex-column ma-1 pa-0 justify-center align-center', 
                               style_='width:170px; height:95px; font-weight:bold; font-size:10pt',
                               outlined=False)]

            for mv_i in self.mv:
                self.matrix_dic[cv_i][mv_i] = TransferChip(mv_i, cv_i)
                self.matrix_dic[cv_i][mv_i].update_meas_figure(self.df)
            
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
    
    def to_identify(self):
        df = self.df.copy()
        self.create_model()

        for cv_i in self.model.cv:
            y_train_df = self.model.identify(df, cv_i)
            if self.train_df.empty:
                self.train_df = y_train_df
            else:
                self.train_df = self.train_df.merge(y_train_df, right_index=True, left_index=True)
            self.to_step_response(cv_i)
        
        self.train_df.index = self.df.index
        self.train_df = self.train_df.merge(self.df[self.model.cv], right_index=True, left_index=True)
        
                
        
            
            
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
                    # chip.create_step_figure(df=ys_df)
                    chip.switch_chip()
                except:
                    chip.switch_chip()
                    chip.children = [chip.no_solution_card]
            
            else:
                chip.disabled = True
                    
            
                    