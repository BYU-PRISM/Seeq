"""
This is a dummy file that contains some functions (it could be classes) to perform backend calculations
"""

from urllib.parse import parse_qs, unquote, urlparse

import numpy as np
import pandas as pd
from seeq import spy


def create_new_signal(signal_a: np.array, signal_b: np.array, index: pd.Index, operation):
    if operation not in ['add', 'subtract', 'multiply', 'divide']:
        raise NameError(f"{operation} is not a supported math operator")
    return pd.DataFrame(getattr(np, operation)(signal_a, signal_b), index=index, columns=['Result'])


def pull_only_signals(url, grid='auto'):
    worksheet = spy.utils.get_analysis_worksheet_from_url(url)
    start = worksheet.display_range['Start']
    end = worksheet.display_range['End']

    search_df = spy.search(url, estimate_sample_period=worksheet.display_range, quiet=True)
    if search_df.empty:
        return pd.DataFrame()
    search_signals_df = search_df[search_df['Type'].str.contains('Signal')]
    
    df = spy.pull(search_signals_df, start=start, end=end, grid=grid, header='ID', quiet=True,
                  status=spy.Status(quiet=True))
    if df.empty:
        return pd.DataFrame()
    df.columns = df.query_df['Name']
    return df


def parse_url(url):
    unquoted_url = unquote(url)
    return urlparse(unquoted_url)


def get_worksheet_url(jupyter_notebook_url):
    parsed = parse_url(jupyter_notebook_url)
    params = parse_qs(parsed.query)
    return f"{parsed.scheme}://{parsed.netloc}/workbook/{params['workbookId'][0]}/worksheet/{params['worksheetId'][0]}"


def get_workbook_worksheet_workstep_ids(url):
    parsed = parse_url(url)
    params = parse_qs(parsed.query)
    workbook_id = None
    worksheet_id = None
    workstep_id = None
    if 'workbookId' in params:
        workbook_id = params['workbookId'][0]
    if 'worksheetId' in params:
        worksheet_id = params['worksheetId'][0]
    if 'workstepId' in params:
        workstep_id = params['workstepId'][0]
    return workbook_id, worksheet_id, workstep_id


def push_signal(df, workbook_id, worksheet_name):
    spy.push(df, workbook=workbook_id, worksheet=worksheet_name, status=spy.Status(quiet=True), quiet=True)
