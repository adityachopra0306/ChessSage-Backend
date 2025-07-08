from datetime import datetime
import numpy as np

def safe_get(d, *keys, default="unknown"):
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, None)
        if d is None:
            return default
    return d


def dates_to_string(obj):
    """
    Recursively converts all UNIX timestamps in nested dicts/lists where key == 'date'
    into formatted date strings. Returns a new object with transformed values.
    """
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            if key == "date" and isinstance(value, int):
                new_obj[key] = datetime.fromtimestamp(value).strftime("%Y-%m-%d")
            else:
                new_obj[key] = dates_to_string(value)
        return new_obj
    elif isinstance(obj, list):
        return [dates_to_string(item) for item in obj]
    else:
        return obj

def num_days_to_words(days):
    '''
    Converts day_count to words, used for Gemini prompting. Returns a string.
    '''
    if days < 30:
        return f"{days} day{'s' if days != 1 else ''}"
    elif days < 365:
        months = round(days / 30)
        return f"{months} month{'s' if months != 1 else ''}"
    else:
        years = round(days / 365)
        return f"{years} year{'s' if years != 1 else ''}"

def date_to_words(given_date):
    '''
    Converts date (datetime object OR str) to day. month and year for use in Gemini prompting. Returns a string.
    '''
    if given_date == "unknown":
        return given_date
    if isinstance(given_date, str):
        given_date = datetime.strptime(given_date, "%Y-%m-%d").date()
    day = given_date.day
    month = given_date.strftime("%B")
    year = given_date.year
    
    date_in_words = f"{day} {month} {year}"
    return date_in_words

def sanitize_numpy_types(obj):
    if isinstance(obj, dict):
        return {k: sanitize_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_numpy_types(v) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_numpy_types(v) for v in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj