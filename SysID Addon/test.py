from seeq import spy

spy.login(username='mbabaei@byu.edu', password='12345678', url='http://prism-seeq-server:34216/')
url = 'http://prism-seeq-server:34216/CFE9A976-1351-40F1-B346-021AD723E578/workbook/B5B92E14-D419-4378-A1DE-' \
      'ABD46E71CEBD/worksheet/EE192A2D-AE95-454C-AD92-14F8A6672212'
worksheet = spy.utils.get_analysis_worksheet_from_url(url)

start = worksheet.display_range['Start']
end = worksheet.display_range['End']

search_df = spy.search(url, estimate_sample_period=worksheet.display_range, quiet=True,
                       status=spy.Status(quiet=True))
spy.push()