import ipyvuetify as v
from .figure_card import FigureCard
import plotly.express as px


# Table Header Class
class TableHeader(v.Card):
    def __init__(self, *args, **kwargs):
        class_ = 'd-flex justify-space-between'
        dense = True
        outlined = False
        elevation = 0
        super().__init__(class_=class_,
                         dense=dense,
                         outlined=outlined,
                         elevation=elevation,
                         *args, **kwargs)

        self.checkbox_header = v.SimpleCheckbox(v_model=False, class_='d-flex justify-center', width='10%',
                                                style_='overflow: hidden')
        self.name_header = v.Card(children=['Name'], background='none', elevation=0, width='55%', class_='px-3 py-1',
                                  style_='font-weight:bold')
        self.unit_header = v.Card(children=['Unit'], background='none', elevation=0, width='15%',
                                  class_='d-flex justify-center px-3 py-1', style_='font-weight:bold')
        self.color_header = v.Card(children=['Color'], background='none', elevation=0, width='15%',
                                   class_='d-flex justify-center py-1', style_='font-weight:bold')
        self.line_style_header = v.Card(children=['Line Style'], background='none', elevation=0, width='20%',
                                        class_='d-flex justify-center py-1 mx-2 px-2', style_='font-weight:bold')

        self.children = [
            v.Card(children=[self.checkbox_header], flat=True, elevation=0, width='7%', class_='d-flex justify-center'),
            v.Divider(vertical=True),
            self.name_header,
            v.Divider(vertical=True),
            self.unit_header,
            v.Divider(vertical=True),
            self.color_header,
            v.Divider(vertical=True),
            self.line_style_header]


# Table Item Class (Row Item)
class TableItem(v.Card):
    item_id = 0
    colors = px.colors.qualitative.Plotly

    def __init__(self, name=None, unit='-', *args, **kwargs):
        rc = ['grey lighten-4', 'white']

        if not name:
            name = 'Data ' + str(TableItem.item_id + 1)
        class_ = 'd-flex justify-space-between'
        color = rc[TableItem.item_id % 2]
        dense = True
        outlined = False
        elevation = 0

        super().__init__(class_=class_,
                         dense=dense,
                         outlined=outlined,
                         elevation=elevation,
                         color=color,
                         *args, **kwargs)

        self.name_item = v.Card(children=[name],
                                color=rc[TableItem.item_id % 2],
                                elevation=0,
                                width='55%',
                                class_='px-3 py-1')

        self.unit_item = v.Card(children=[unit],
                                color=rc[TableItem.item_id % 2],
                                elevation=0,
                                width='15%',
                                class_='d-flex justify-center px-3 py-1',
                                align_center=True)

        self.color_item = v.Card(children=[v.Icon(children=['mdi-checkbox-blank'],
                                                  color=TableItem.colors[TableItem.item_id % 10],
                                                  class_='',
                                                  dense=True)],
                                 color=rc[TableItem.item_id % 2],
                                 elevation=0,
                                 width='15%',
                                 class_='d-flex justify-center py-1')

        self.style_item = Line_Style(idx=TableItem.item_id,
                                     style_='font-weight:bold; height:26px; width:20%; overflow: hidden hidden'
                                     )

        self.checkbox_item = v.SimpleCheckbox(v_model=False, class_='d-flex justify-left', width='10%',
                                              style_='overflow: hidden', model_id='{}'.format(TableItem.item_id))

        self.children = [v.Card(children=[self.checkbox_item], elevation=0, width='7%', class_='d-flex justify-center',
                                color=rc[TableItem.item_id % 2]),
                         v.Divider(vertical=True),
                         self.name_item,
                         v.Divider(vertical=True),
                         self.unit_item,
                         v.Divider(vertical=True),
                         self.color_item,
                         v.Divider(vertical=True),
                         self.style_item
                         ]

        TableItem.item_id += 1

    # Reset Tag ID
    @staticmethod
    def reset():
        TableItem.item_id = 0


# Table Class (TableHeader + TableItem)
class TableCard(v.Card):
    def __init__(self, *args, **kwargs):
        TableItem().reset()
        width = '100%'
        flat = False
        elevation = 5
        class_ = 'pa-4 ma-4'
        style_ = 'border-radius:12px; overflow:hidden auto; height:32%'
        super().__init__(
            width=width,
            flat=flat,
            class_=class_,
            style_=style_,
            elevation=elevation,
            *args, **kwargs)
    
        self.table_header = TableHeader()
        self.items_list = []
        self.empty_table = v.Row(children=['No Data Available'], class_='d-flex justify-center pa-1 pt-3')

        self.children = [self.table_header, v.Divider(), self.empty_table]

    def create_table(self, items_list):
        self.items_list = items_list
        table = [self.table_header, v.Divider()] + items_list
        self.children = table


class Line_Style(v.Select):
    def __init__(self, idx=None, style_=None, *args, **kwargs):
        super().__init__(style_=style_,
                         *args, **kwargs)

        self.items = ['____', '_ _ _', '.....', '_ . _']
        self.v_model = self.items[0]

        self.style_dict = {'____': 'solid', '_ _ _': 'dash', '_ . _': 'dashdot', '.....': 'dot'}
        self.dense = True
        self.class_ = 'px-2 mx-2'
        self.idx = idx

    def get_style(self):
        return self.style_dict[self.v_model]
