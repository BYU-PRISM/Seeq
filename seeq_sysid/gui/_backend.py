"""
This file contains some functions (it could be classes) to perform backend calculations
"""

from urllib.parse import parse_qs, unquote, urlparse
from IPython.display import clear_output

from pandas import DataFrame
from seeq import spy


def pull_signals(url, grid='auto'):
    worksheet = spy.utils.get_analysis_worksheet_from_url(url)
    start = worksheet.display_range['Start']
    end = worksheet.display_range['End']

    search_df = spy.search(url, estimate_sample_period=worksheet.display_range, quiet=True,
                           status=spy.Status(quiet=True))
    capsules_list = search_df[search_df['Type'].str.contains('CalculatedCondition')]['Name'].to_list()
    signal_list = search_df[search_df['Type'].str.contains('Signal')]['Name'].to_list()

    if search_df.empty:
        return DataFrame(), DataFrame(), DataFrame()
    search_all_df = search_df[search_df['Type'].str.contains('al')]

    all_df = spy.pull(search_all_df, start=start, end=end, grid=grid, header='ID', quiet=True,
                      status=spy.Status(quiet=True))
    if all_df.empty:
        return DataFrame(), DataFrame(), DataFrame()
    
    if hasattr(all_df, 'spy') and hasattr(all_df.spy, 'query_df'):
        all_df.columns = all_df.spy.query_df['Name']
    elif hasattr(all_df, 'query_df'):
        all_df.columns = all_df.query_df['Name']
    else:
        raise AttributeError(
            "A call to `spy.pull` was successful but the response object does not contain the `spy.query_df` property "
            "required for `seeq.addons.correlation")

    all_df.dropna(inplace=True)
    signal_df = all_df[signal_list]
    if signal_df.empty:
        return DataFrame(), DataFrame(), DataFrame()
    capsule_df = all_df[capsules_list]
    if capsule_df.empty:
        return signal_df, DataFrame(), search_df
    signal_df.columns = signal_list
    capsule_df.columns = capsules_list

    clear_output()

    return signal_df, capsule_df, search_df


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


def push_formula(df, formula, workbook_id, worksheet_name):
    spy.push(data=df, metadata=formula, workbook=workbook_id, worksheet=worksheet_name, status=spy.Status(quiet=True),
             quiet=True)
