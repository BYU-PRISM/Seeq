import ipyvuetify as v
import ipywidgets as widgets

from gekko import GEKKO
# from statsmodels.tsa.stattools import grangercausalitytests

from copy import deepcopy
from pathlib import Path


from seeq_sysid._backend import push_formula, pull_signals, parse_url, get_worksheet_url, \
    get_workbook_worksheet_workstep_ids, create_formula_variable_name

from seeq_sysid.left_panel import Left_Panel
from seeq_sysid.figure_panel import Figure_Table
from seeq_sysid.model_obj import Model_Obj, ARX, Subspace, NN
from seeq_sysid.panels import Arx_Panel, SS_Panel, NN_Panel
from seeq_sysid.utils import create_eq
from seeq_sysid._plot import Figure_Card
