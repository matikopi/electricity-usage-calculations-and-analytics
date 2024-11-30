from datetime import datetime, timedelta

def get_past_dates(days):
    """
    Generates a list of dates from today going back a specified number of days.

    Parameters:
    days (int): The number of days to go back from today.
                For example, if days = 7, the function will return dates for the past 7 days including today.

    Returns:
    list of datetime.date: A list of datetime.date objects from today going backwards
                           by the specified number of days.
                           The list includes today's date as the first element.
    """
    today = datetime.now().date()
    date_list = [today - timedelta(days=i) for i in range(days + 1)]
    return date_list

