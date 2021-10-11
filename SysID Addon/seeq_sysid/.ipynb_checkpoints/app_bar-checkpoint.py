import ipyvuetify as v
import ipywidgets as widgets
from pathlib import Path
from seeq_sysid.utils import add_tooltip


class HamburgerMenu(v.Menu):
    def __init__(self, **kwargs):
        self.hamburger_button = v.AppBarNavIcon(v_on='menuData.on', class_='align-center ma-2 mt-3')
        self.feedback_button = v.ListItem(value='help',
                                          ripple=True,
                                          href='mailto: support@company.com?subject=MyAddOn Feedback',
                                          children=[v.ListItemAction(class_='mr-2 ml-0',
                                                                     children=[v.Icon(color='#212529',
                                                                                      children=['fa-life-ring'])]),
                                                    v.ListItemActionText(children=[f'Send Support Request'])
                                                    ])

        self.user_guide_button = v.ListItem(value='tutorial',
                                            ripple=True,
                                            href='https://github.com/BYU-PRISM/Seeq',
                                            target='_blank',
                                            children=[v.ListItemAction(class_='mr-2 ml-0',
                                                                       children=[v.Icon(color='#212529',
                                                                                        children=['mdi-help-box'])]),
                                                      v.ListItemActionText(children=[f'User Guide'])
                                                      ])

        self.items = [v.Divider(), self.feedback_button, v.Divider(), self.user_guide_button, v.Divider()]

        super().__init__(offset_y=True,
                         offset_x=False,
                         dense=True,
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


class App_Bar(v.Card):
    def __init__(self, tabs: list = [], items: list = [], logo_name=Path(__file__).parent / 'data/seeq_logo.png',
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add-on logo (.png)
        file = open(logo_name, 'rb')
        image = file.read()
        self.image = widgets.Image(value=image, format='png', align='center')
        file.close()

        self.logo = [v.Img(children=[self.image], class_='align-center mt-2 pl-4')]

        self.load_worksheet = v.Btn(icon=True, children=[v.Icon(children=['mdi-folder-search-outline'])],
                                    class_='align-center ma-2 mt-3')
        self.load_worksheet.on_event('click', self.load_worksheet_action)

        self.close_url_dialog_btn = v.Btn(children=['CLOSE'], color='#007960', text=True)
        self.close_url_dialog_btn.on_event('click', self.close_url_action)

        self.ok_url_dialog_btn = v.Btn(children=['OK'], color='#007960', text=True, loading=False)
        self.ok_url_dialog_btn.on_event('click', self.ok_url_action)

        self.worksheet_url = v.TextField(v_model='', placeholder='Worksheet URL', class_='mx-4', color='#007960',
                                         clearable=True)

        control_dialog_btn_layout = v.Layout(children=[v.Spacer(), self.close_url_dialog_btn, self.ok_url_dialog_btn])

        dialog_card_content = [v.CardTitle(children=['Please Enter a Worksheet URL:']),
                               self.worksheet_url,
                               control_dialog_btn_layout]

        dialog_card = v.Card(children=dialog_card_content, class_='pa-2 ma-3 my-0', flat=True)

        self.url_dialog = v.Dialog(name='OpneWB',
                                   children=[v.Card(children=[dialog_card])],
                                   v_model=False,
                                   max_width='600px')

        self.url_dialog.on_event('keydown.stop', lambda *args: None)

        self.ham_menu = HamburgerMenu()

        
        # Adding Tooltips (tt = with tooltip)
        self.load_worksheet_tt = add_tooltip(self.load_worksheet, 'Open Worksheet')
        
        
        
        
        
        
        
        
        app = v.Tabs(children=self.logo +
                              tabs + items +
                              [v.Spacer(),
                               self.url_dialog,
                               self.load_worksheet_tt,
                               v.Divider(vertical=True, inset=True),
                               self.ham_menu],
                     color='#1d376c',
                     class_='align-center pt-0',
                     slider_size='4',
                     background_color='grey lighten-4',
                     hide_slider=True,
                     height=60,
                     style_='width:98%; border-radius:12px')

        self.children = [app]

    def load_worksheet_action(self, *args):
        self.url_dialog.v_model = True

    def close_url_action(self, *args):
        self.url_dialog.v_model = None

    def ok_url_action(self, *args):
        self.url_dialog.v_model = None
