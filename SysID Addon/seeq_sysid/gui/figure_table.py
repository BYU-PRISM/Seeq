import ipyvuetify as v

from seeq_sysid.gui.table_card import Table_Card, Table_Item, Table_Header
from seeq_sysid.gui.figure_card import Figure_Card


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
