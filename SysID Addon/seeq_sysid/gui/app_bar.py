import ipyvuetify as v
import ipywidgets as widgets
from pathlib import Path
from .utils import add_tooltip


class HamburgerMenu(v.Menu):
    """
    Create a Hamburger Menu in the right corner of App Bar
    """

    def __init__(self, **kwargs):
        # Create menu icon button
        self.hamburger_button = v.AppBarNavIcon(v_on='menuData.on', class_='align-center mb-2 mt-3 ml-3 mr-0')
        
        
        # load worksheet option
        self.load_worksheet = v.ListItem(value='open',
                                         children=[v.ListItemAction(class_='mr-2 ml-0',
                                                                       children=[v.Icon(color='#212529',
                                                                                        children=['mdi-folder-search-outline'])]),
                                                      v.ListItemActionText(children=[f'Open Worksheet'])
                                                      ])
        

        # Feedback option
        self.feedback_button = v.ListItem(value='help',
                                          ripple=True,
                                          href='https://github.com/BYU-PRISM/Seeq/issues',
                                          children=[v.ListItemAction(class_='mr-2 ml-0',
                                                                     children=[v.Icon(color='#212529',
                                                                                      children=['fa-life-ring'])]),
                                                    v.ListItemActionText(children=[f'Send Support Request'])
                                                    ])
        # GitHub page
        self.user_guide_button = v.ListItem(value='tutorial',
                                            ripple=True,
                                            href='https://github.com/BYU-PRISM/Seeq',
                                            target='_blank',
                                            children=[v.ListItemAction(class_='mr-2 ml-0',
                                                                       children=[v.Icon(color='#212529',
                                                                                        children=['mdi-help-box'])]),
                                                      v.ListItemActionText(children=[f'User Guide'])
                                                      ])
        
        
        
        # Open Worksheet Dialog & Events
        self.load_worksheet.on_event('click', self.load_worksheet_action)

        self.close_url_dialog_btn = v.Btn(children=['CLOSE'], color='#007960', text=True)
        self.close_url_dialog_btn.on_event('click', self.close_url_action)

        self.ok_url_dialog_btn = v.Btn(children=['OK'], color='#007960', text=True, loading=False)
        self.ok_url_dialog_btn.on_event('click', self.ok_url_action)
        # Create a text field for the worksheet url
        self.worksheet_url = v.TextField(v_model='', placeholder='Worksheet URL', class_='mx-4', color='#007960',
                                         clearable=True)
        self.worksheet_url.on_event('paste.stop', lambda *args: None)

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
        
        
        self.items = [self.load_worksheet, v.Divider(), self.feedback_button, v.Divider(), self.user_guide_button, self.url_dialog]

        super().__init__(offset_y=True,
                         offset_x=False,
                         dense=True,
                         right=True,
                         class_='ma-0 pa-0',
                         v_slots=[{
                             'name': 'activator',
                             'variable': 'menuData',
                             'children': self.hamburger_button
                         }],
                         children=[
                             v.List(children=self.items)
                         ],
                         **kwargs)
        
        
    # Load worksheet event functions
    def load_worksheet_action(self, *args):
        self.url_dialog.v_model = True

    def close_url_action(self, *args):
        self.url_dialog.v_model = None

    def ok_url_action(self, *args):
        self.url_dialog.v_model = None


class AppBar(v.Card):
    """
    Create app bar for the Add-on. This app bar includes icon, tabs, load worksheet button and, hamburger menu.
    """

    def __init__(self, tabs=None, items=None, title_list=None, logo_name=Path(__file__).parent / '../data/seeq_logo.png', *args,
                 **kwargs):
        """
        Args:
            tabs : list of tabs
            items : list of items (app sheet)
            logo_name : App icon directory
        """
        super().__init__(flat=True, elevation=0, shadow=False, *args, **kwargs)
            
        # read add-on logo (.png)
        file = open(logo_name, 'rb')
        image = file.read()
        self.image = widgets.Image(value=image, format='png', align='center')
        file.close()

        self.logo = [v.Img(children=[self.image], class_='align-center pl-4')]
        
        self.title = v.Text(children=[''], style_='font-size:18pt ; font-weight:bold', class_='d-flex justify-end align-center')
        
        self.ham_menu = HamburgerMenu()
        
        self.next_btn = v.Btn(children=['Next >'], 
                  class_='ma-2 mt-3 mr-3 white--text',
                  bold=True,
                  color='#1D376C',
                  style_='font-weight:bold; width:80px; text-transform:none',
                  dark=False)

        self.back_btn = v.Btn(children=['< Back'], 
                  class_='ma-2 mt-3 ml-3',
                  bold=True,
                  color='#1D376C',
                  style_='font-weight:bold; width:80px; text-transform:none; background-color:none',
                  outlined=True,
                  dark=True,
                  disabled=False)
        
        self.push_btn = v.Btn(children=['Push'],
                              class_='ma-2 mt-3 mr-3 white--text',
                              bold=True,
                              color='#1D376C',
                              style_='font-weight:bold; width:80px; text-transform:none',
                              dark=False)
        
        self.nav_btn = v.Layout(children=[self.back_btn, self.next_btn], class_='d-flex justify-end align-center ma-2')

        if items is None:
            items = []
        if tabs is None:
            tabs = []
        if title_list is None:
            self.nav_btn = v.Layout()
            self.title_list = []
        else:
            self.title_list = title_list
    
        self.tabs = v.Tabs(children=[self.ham_menu] + self.logo + tabs + [self.title] + items + [self.nav_btn],
                     color='#1d376c',
                     class_='align-center pt-0',
                     slider_size='4',
                     background_color='grey lighten-4',
                     hide_slider=True,
                     height=60,
                     style_='width:98%; border-radius:12px')

        self.children = [self.tabs]

