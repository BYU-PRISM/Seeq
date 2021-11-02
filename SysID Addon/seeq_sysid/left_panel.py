import ipyvuetify as v
import ipywidgets as widgets


class Left_Panel(v.Card):
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

    def __init__(self,
                 model_name='Sys-Ident',
                 style_='width: 330px; min-height:94%; height:94%; max-height:98%; font-weight:bold; color:white;'
                        ' font-size:16px; border-radius:12px',
                 class_='pa-4 ma-4 ml-0 pl-7 pr-7',
                 color='#007960',
                 outlined=False,
                 shaped=False,
                 elevation=10,
                 dense=True,
                 children=None,
                 *args,
                 **kwargs):
        if children is None:
            children = []
        self.model_name = model_name

        super().__init__(tag=model_name,
                         style_=style_,
                         class_=class_,
                         color=color,
                         outlined=outlined,
                         shaped=shaped,
                         elevation=elevation,
                         dense=dense,
                         children=children,
                         *args,
                         **kwargs)

        # Icons
        title_icon = v.Icon(class_='', children=['mdi-tools'], color='white')

        # Drop Downs
        self.mv_select = v.Select(tag='Manipulated Variables',
                                  v_model=[],
                                  items=[],
                                  color=self.colors['seeq_primary'],
                                  item_color=self.colors['seeq_primary'],
                                  dense=True,
                                  outlined=True,
                                  class_='d-flex justify-center',
                                  style_='width: 280px; font-size:14px',
                                  filled=True,
                                  background_color='white',
                                  placeholder='Select',
                                  multiple=True,
                                  clearable=True,
                                  solo=True)

        self.cv_select = v.Select(tag='Measured Variables',
                                  v_model=[],
                                  items=[],
                                  color=self.colors['seeq_primary'],
                                  item_color=self.colors['seeq_primary'],
                                  dense=True,
                                  class_='d-flex justify-center',
                                  style_='width: 280px; font-size:14px',
                                  outlined=True,
                                  filled=True,
                                  background_color='white',
                                  placeholder='Select',
                                  multiple=True,
                                  clearable=True,
                                  solo=True)

        self.train_condition = v.Select(tag='Training Condition',
                                        v_model=[],
                                        items=[],
                                        color=self.colors['seeq_primary'],
                                        item_color=self.colors['seeq_primary'],
                                        dense=True,
                                        outlined=False,
                                        class_='d-flex justify-center',
                                        style_='width: 280px; font-size:14px',
                                        filled=True,
                                        background_color='white',
                                        placeholder='All Data',
                                        multiple=True,
                                        rounded=True,
                                        clearable=True,
                                        solo=True)

        self.validation_condition = v.Select(tag='Validation Condition',
                                             v_model=[],
                                             items=[],
                                             color=self.colors['seeq_primary'],
                                             item_color=self.colors['seeq_primary'],
                                             dense=True,
                                             class_='d-flex justify-center',
                                             style_='width: 280px; font-size:14px',
                                             outlined=False,
                                             filled=True,
                                             background_color='white',
                                             placeholder='All Data',
                                             multiple=True,
                                             rounded=True,
                                             clearable=True,
                                             solo=True)

        # Buttons
        self.identify_model_btn = v.Btn(name='identification button',
                                        style_='color:#007960; font-size:9pt; font-weight:bold; width:130px',
                                        color='white',
                                        class_='mb-4',
                                        dense=True,
                                        elevation=4,
                                        children=['Identify Model'],
                                        disabled=True)

        self.push_model_btn = v.Btn(name='identification button',
                                    style_='color:#007960; font-size:9pt; font-weight:bold; width:130px',
                                    color='white',
                                    class_='mb-4',
                                    dense=True,
                                    elevation=4,
                                    children=['Push Model'],
                                    disabled=True)

        # Card
        self.identify_push_card = v.Card(children=[self.identify_model_btn, self.push_model_btn],
                                         style_='background:none', flat=True, class_='d-flex justify-space-between')

        # Title
        self.title = v.Card(class_='pt-5 mb-7 mx-0 d-flex justify-left', style_='font-size:20px; background:none',
                            dark=True, center=True, align='center', flat=True,
                            children=[title_icon, v.Divider(vertical=True, class_='mx-2'),
                                      "{} Settings".format(model_name)])

        # Set Tooltips

        # Set Panel Children
        self.children = [self.title,
                         'Manipulated Variables (MV)', self.mv_select,
                         'Measured Variables (CV)', self.cv_select,
                         v.Divider(class_='mb-4'),
                         'Training Conditions', self.train_condition,
                         'Validation Conditions', self.validation_condition,
                         v.Divider(class_='mb-4'),
                         self.identify_push_card]
