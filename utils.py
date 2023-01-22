"""
Traduce i nomi dei mesi da italiano ad inglese, verrà applicata al dafataframe
"""
def translate_time(timestamp: str):
    MONTH_CODE = {'gen': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'apr': 'Apr', 'mag': 'May', 'giu': 'Jun', 'lug': 'Jul', 'ago': 'Aug', 'set': 'Sep', 'ott': 'Oct', 'nov': 'Nov', 'dic': 'Dec'}

    date, time = timestamp.split(",")
    month = date.split(" ")[1]
    
    if month in MONTH_CODE.keys() and not month[0].isdigit():
        date = date.replace(month, MONTH_CODE[month])
    else:
        return None
    date = date.replace(" ", "").strip()
    time = time[:-4].strip()

    return date + " " + time

