# Custom
from ipywidgets import HTMLMath, Layout
from ipyvuetify import Tooltip


def create_eq(text, color, fontsize, top='10px', bot=''):
    return HTMLMath(value=f"<b><font color={color}><font size={fontsize}>{text}</b>",layout=Layout(top=top,bottom=bot))


def add_tooltip(item, text):
    item.v_on = 'tooltip.on'
    return Tooltip(bottom=True, v_slots=[{
        'name': 'activator',
        'variable': 'tooltip',
        'children': item,
    }], children=[text])
    