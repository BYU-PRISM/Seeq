import ipyvuetify as v
from seeq_sysid._plot import Figure_Card
import plotly.express as px


# Table Header Class
class Table_Header(v.Card):
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
class Table_Item(v.Card):
    item_id = 0
    colors = px.colors.qualitative.Plotly

    def __init__(self, name=None, unit='-', *args, **kwargs):
        rc = ['grey lighten-4', 'white']

        if not name:
            name = 'Data ' + str(Table_Item.item_id + 1)
        class_ = 'd-flex justify-space-between'
        color = rc[Table_Item.item_id % 2]
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
                                color=rc[Table_Item.item_id % 2],
                                elevation=0,
                                width='55%',
                                class_='px-3 py-1')

        self.unit_item = v.Card(children=[unit],
                                color=rc[Table_Item.item_id % 2],
                                elevation=0,
                                width='15%',
                                class_='d-flex justify-center px-3 py-1',
                                align_center=True)

        self.color_item = v.Card(children=[v.Icon(children=['mdi-checkbox-blank'],
                                                  color=Table_Item.colors[Table_Item.item_id % 10],
                                                  class_='',
                                                  dense=True)],
                                 color=rc[Table_Item.item_id % 2],
                                 elevation=0,
                                 width='15%',
                                 class_='d-flex justify-center py-1')

        self.style_item = Line_Style(idx=Table_Item.item_id,
                                     style_='font-weight:bold; height:26px; width:20%; overflow: hidden hidden'
                                     )

        self.checkbox_item = v.SimpleCheckbox(v_model=False, class_='d-flex justify-left', width='10%',
                                              style_='overflow: hidden', model_id='{}'.format(Table_Item.item_id))

        self.children = [v.Card(children=[self.checkbox_item], elevation=0, width='7%', class_='d-flex justify-center',
                                color=rc[Table_Item.item_id % 2]),
                         v.Divider(vertical=True),
                         self.name_item,
                         v.Divider(vertical=True),
                         self.unit_item,
                         v.Divider(vertical=True),
                         self.color_item,
                         v.Divider(vertical=True),
                         self.style_item
                         ]

        Table_Item.item_id += 1

    # Reset Tag ID
    @staticmethod
    def reset():
        Table_Item.item_id = 0


# Table Class (Table_Header + Table_Item)
class Table_Card(v.Card):
    def __init__(self, *args, **kwargs):
        Table_Item().reset()
        width = '60%'
        flat = False
        elevation = 5
        class_ = 'pa-4 ma-4'
        style_ = 'border-radius:12px; overflow:hidden auto; height:30%'
        super().__init__(width=width,
                         flat=flat,
                         class_=class_,
                         style_=style_,
                         elevation=elevation,
                         *args, **kwargs)

        self.table_header = Table_Header()
        self.items_list = []
        self.empty_table = v.Row(children=['No Data Available'], class_='d-flex justify-center pa-1 pt-3')

        self.children = [self.table_header, v.Divider(), self.empty_table]

    def on_click_item(item, *_):
        print(item.owner.model_id)

    def create_table(self, items_list):
        self.items_list = items_list
        table = [self.table_header, v.Divider()] + items_list
        self.children = table


# Visualization Class (Figures+Table)
class Figure_Table(v.Layout):
    def __init__(self, *args, **kwargs):
        class_ = 'd-flex flex-column justify-right ml-1'
        style_ = 'width:100%; height:100%'
        super().__init__(class_=class_,
                         style_=style_,
                         *args, **kwargs)

        self.figure = Figure_Card()
        self.table = Table_Card()

        self.children = [self.figure, self.table]

        self.table.table_header.checkbox_header.observe(self.header_checkbox_action, names=['v_model'])

    def header_checkbox_action(self, item, *_):
        all_value = item.owner.v_model
        for tag in self.table.items_list:
            tag.checkbox_item.v_model = all_value

    def create(self, train_df, validation_df, units=None):
        Table_Item().reset()
        self.table.table_header.checkbox_header.v_model = False

        if not units:
            units = {}
            for tag in train_df.columns:
                units[tag] = '-'

        # create plots
        self.figure.plot(train_df=train_df, validation_df=validation_df)

        # create table
        items_list = []
        for name in train_df.columns:
            temp_item = Table_Item(name=name, unit=units[name])
            temp_item.checkbox_item.observe(self.update_visibility, names=['v_model'])
            temp_item.style_item.on_event('change', self.update_line_style)
            items_list += [temp_item]

        self.table.create_table(items_list)

    def update_visibility(self, item, *_):
        idx = int(item.owner.model_id)
        status = item.owner.v_model

        self.figure.update(idx=idx, status=status)

    def update_line_style(self, item, *_):
        idx = item.idx
        line_style = item.get_style()
        self.figure.update(idx=idx, line_style=line_style)


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
