import ipyvuetify as v

from .table_card import TableCard, TableItem, TableHeader
from .figure_card import FigureCard

from pandas import DataFrame


# Visualization Class (Figures+Table)
class FigureTable(v.Card):
    def __init__(self, 
                 class_ = 'd-flex flex-column justify-start align-center ml-1 mr-1',
                 style_ = 'width:100%; height:100%',
                 *args, **kwargs):

        super().__init__(class_=class_,
                         style_=style_,
                         flat=True,
                         *args,
                         **kwargs)

        self.figure = FigureCard()
        self.table = TableCard()

        self.children = [self.figure, self.table]

        self.table.table_header.checkbox_header.observe(self.header_checkbox_action, names=['v_model'])

    def header_checkbox_action(self, item, *_):
        all_value = item.owner.v_model
        for tag in self.table.items_list:
            tag.checkbox_item.v_model = all_value

    def create(self, train_df=DataFrame(), validation_df=DataFrame(), units=None):
        TableItem().reset()
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
            temp_item = TableItem(name=name, unit=units[name])
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
