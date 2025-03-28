from datetime import date

import pandas as pd


# TODO: Modify for other datasets
def get_date_range(dataset):
    dataset = dataset.lower()
    date_ranges = {"seas5": {"start_date": "1981-01-01"}}
    start_date = date_ranges[dataset]["start_date"]
    today = date.today()
    if today.day <= 6:
        if today.month == 1:
            end_date = date(today.year - 1, 12, 1)
        else:
            end_date = date(today.year, today.month - 1, 1)
    else:
        end_date = date(today.year, today.month, 1)

    date_range = pd.date_range(start=start_date, end=end_date, freq="MS")

    date_strings = [d.strftime("%Y-%m-%d") for d in date_range]
    date_strings.sort(reverse=True)
    return date_strings
