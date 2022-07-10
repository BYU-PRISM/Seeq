import ipyvuetify as v
from ipywidgets import HTML


class Setup(v.Card):  
    colors = {
        'app_bar': '#007960',
        'controls_background': '#F6F6F6',
        'visualization_background': '#FFFFFF',
        'seeq_primary': '#007960',
    }

    additional_styles = HTML("""
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
    
    
    def __init__(self):
        super().__init__()
        self.class_ = 'd-flex flex-column ma-0 pa-0 align-content-center flex-wrap justify-space-around'
        self.style_ = 'width:100%; min-height:750px; height:100%; background-color:#1D376C'

        
        # Select MV and CV
        self.mv_title = v.Text(children=['Manipulated Variables (MV)'], style_='font-size:12pt; font-weight:bold')
        self.mv_select = v.Select(tag='Manipulated Variables',
                                  v_model=[],
                                  items=[],
                                  color=self.colors['seeq_primary'],
                                  item_color=self.colors['seeq_primary'],
                                  dense=True,
                                  outlined=False,
                                  class_='d-flex justify-center mt-1',
                                  style_='width: 100%; font-size:14px',
                                  filled=True,
                                  background_color='#EDF4FF',
                                  placeholder='Select',
                                  multiple=True,
                                  clearable=True,
                                  solo=True)
        
        self.cv_title = v.Text(children=['Measured Variables (CV)'], style_='font-size:12pt; font-weight:bold')
        self.cv_select = v.Select(tag='Measured Variables',
                          v_model=[],
                          items=[],
                          color=self.colors['seeq_primary'],
                          item_color=self.colors['seeq_primary'],
                          dense=True,
                          class_='d-flex justify-center mt-1',
                          style_='width: 100%; font-size:14px',
                          outlined=False,
                          filled=True,
                          background_color='#EDF4FF',
                          placeholder='Select',
                          multiple=True,
                          clearable=True,
                          solo=True)
        
        
        
        # Select Train Condition and Validation Condition
        self.train_condition_title = v.Text(children=['Training Conditions'], style_='font-size:12pt; font-weight:bold')
        self.train_condition_select = v.Select(tag='Training Conditions',
                                               v_model=[],
                                               items=[],
                                               color=self.colors['seeq_primary'],
                                               item_color=self.colors['seeq_primary'],
                                               dense=True,
                                               outlined=False,
                                               class_='d-flex justify-center mt-1',
                                               style_='width: 100%; font-size:14px',
                                               filled=True,
                                               background_color='#EDF4FF',
                                               placeholder='Select',
                                               multiple=True,
                                               clearable=True,
                                               solo=True)
        
        self.valid_condition_title = v.Text(children=['Validation Conditions'], style_='font-size:12pt; font-weight:bold')
        self.valid_condition_select = v.Select(tag='Validation Conditions',
                                               v_model=[],
                                               items=[],
                                               color=self.colors['seeq_primary'],
                                               item_color=self.colors['seeq_primary'],
                                               dense=True,
                                               class_='d-flex justify-center mt-1',
                                               style_='width: 100%; font-size:14px',
                                               outlined=False,
                                               filled=True,
                                               background_color='#EDF4FF',
                                               placeholder='Select',
                                               multiple=True,
                                               clearable=True,
                                               solo=True)
        
        
        self.select_card = v.Card(children=[self.mv_title, self.mv_select,
                                            self.cv_title, self.cv_select,
                                            self.train_condition_title, self.train_condition_select,
                                            self.valid_condition_title, self.valid_condition_select],
                                  class_='ma-2 pa-2 justify-center', 
                                  style_='width:98%', 
                                  flat=True, elevation=0)
        
        # Navigation Buttons
        self.next_btn = v.Btn(children=['Next >'], 
                              class_='d-flex ma-2 justify-end white--text',
                              bold=True,
                              color='#1D376C',
                              style_='font-weight:bold; width:80px; text-transform:none;',
                              dark=False,
                              disabled=True)
        self.next_btn_container = v.Layout(children=[v.Spacer(), self.next_btn], class_='d-flex flex-column justify-end align-end')
        
        self.items_card = v.Card(children=[self.select_card], class_='pa-2 ma-2 align-center', style_='width:30%; max-height:450px')
        
        self.signal = []
        self.capsules = []
        
        self.children=[self.items_card]
        
    # Functions
    def get_data(self):
        return (self.mv_select.v_model, self.cv_select.v_model)
    
    def set_data(self, signals: list=[], capsules: list=[]):
        self.mv_select.items = signals
        self.cv_select.items = signals
        
        self.train_condition_select.items = capsules
        self.valid_condition_select.items = capsules

        self.signal = signals
        self.capsules = capsules
