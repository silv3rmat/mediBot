from datetime import datetime

def polish_date_to_datetime(date_string):
    values = date_string.split(' ')
    day = int(values[0])
    months ={
        'styczeń': 1,
        'stycznia': 1,
        'luty': 2,
        'lutego': 2,
        'marzec': 3,
        'marca': 3,
        'kwiecień': 4,
        'kwietnia': 4,
        'maj': 5,
        'maja': 5,
        'czerwiec': 6,
        'czerwca': 6,
        'lipiec': 7,
        'lipca': 7,
        'sierpień': 8,
        'sierpnia': 8,
        'wrzesień': 9,
        'września': 9,
        'październik': 10,
        'października': 10,
        'listopad': 11,
        'listopada': 11,
        'grudzień': 12,
        'grudnia': 12
    }
    month = months[values[1].lower()]
    year = int(values[2][:-1])
    return datetime(year=year, month=month, day=day).strftime('%d-%m-%Y')
