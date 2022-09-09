import json
import pandas as pd
import matplotlib.pyplot as plot


def load_data():
    json_data = None
    with open("data.json", "r", encoding="utf-8") as fp:
        file_content = fp.read()
        json_data = json.loads(file_content)
        fp.close()
    with open("data2.json", "r", encoding="utf-8") as fp:
        file_content = fp.read()
        for video in json.loads(file_content):
            if len(video['title']) >=3 and len(video['channel']) >= 3:
                json_data.append(video)
        fp.close()
    return json_data

def get_barplot_data(data):
    barplot_data = {}
    for d in data:
        channel_name = d['channel']
        if channel_name in barplot_data.keys():
            barplot_data[channel_name] += 1
        else:
            barplot_data[channel_name] = 1
    return barplot_data

#MOST VIEWED CHANNELS BAR PLOT
def show_barplot(data_frame):

    data_frame = data_frame.groupby('channel')['channel'].count().reset_index(name='views')
    data_frame = data_frame[data_frame['views'] > 20]
    data_frame = data_frame.sort_values('views', ascending=False)
    data_frame.head(20).plot.bar(x="channel", y="views", title="Most Viewed Channels", figsize=(50, 50))
    plot.subplots_adjust(bottom=.3)
    plot.show(block=True)

def convert_time(timestamp:str):
    #translates italian months to english
    MONTH_CODE = {'gen': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'apr': 'Apr', 'mag': 'May', 'giu': 'Jun', 'lug': 'Jul', 'ago': 'Aug', 'set': 'Sep', 'ott': 'Oct', 'nov': 'Nov', 'dic': 'Dec'}
    
    date, time = timestamp.split(",")
    month = date.split(" ")[1]
    
    if month in MONTH_CODE.keys():
        date = date.replace(month, MONTH_CODE[month])
    date = date.replace(" ", "").strip()
    time = time[:-4].strip()

    return date + " " + time

def set_hours(hour):
    hour = str(hour)
    if len(hour) == 1:
        hour = "0" + hour
    hour += ":00"
    return hour

def create_pandas_data_frame(data):
    data_frame = pd.DataFrame(data)
    data_frame['timestamp'] = data_frame['timestamp'].apply(convert_time)
    data_frame['timestamp'] = pd.to_datetime( data_frame['timestamp'], format='%d%b%Y %H:%M:%S')
    return data_frame

def show_hours_views(data_frame):
    #data_frame = pd.DataFrame(data)
    #data_frame['timestamp'] = data_frame['timestamp'].apply(convert_time)
    
    #data_frame['timestamp'] = pd.to_datetime( data_frame['timestamp'], format='%d%b%Y %H:%M:%S')
    data_frame['timestamp'] = data_frame['timestamp'].dt.hour
    data_frame['timestamp'] = data_frame['timestamp'].apply(set_hours)
    
    data_frame = data_frame.groupby("timestamp").size().reset_index(name='count')
    data_frame.plot.bar(x="timestamp", y="count")
    plot.show(block=True)


# def create_animated_dataframe(data_frame):
#     new_data_frame = data_frame.sort_values('timestamp')
#     #adding date info to column
#     new_data_frame['only_date'] = pd.to_datetime(new_data_frame['timestamp'].dt.strftime('%d%b%Y'), format='%d%b%Y')
    
#     #counting number of video watched in a day
#     new_data_frame = new_data_frame.groupby(['channel', 'only_date']).size().reset_index(name="count").sort_values( ['channel', 'only_date'],ascending=True)
#     #counting number of video watched in a month
#     new_data_frame['only_date'] = pd.to_datetime(new_data_frame['only_date'].dt.strftime('%b%Y'), format='%b%Y')
#     new_data_frame = new_data_frame.groupby(['channel', 'only_date']).size().reset_index(name="count").sort_values( ['channel', 'only_date'],ascending=True)
#     #adding cumulative number of videos
#     new_data_frame['cumulative'] = new_data_frame.groupby(['channel']).cumsum()
    

# def create_animated_plot(data_frame):
#     data_frame.plot_animated('tets.gif', period_fmt="%b%Y", title="ciao")

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    data = load_data()
    data_frame = create_pandas_data_frame(data)
    show_barplot(data_frame)
    show_hours_views(data_frame)
    

        
    