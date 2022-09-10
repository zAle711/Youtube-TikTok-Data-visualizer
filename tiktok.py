import pandas as pd
import json
import matplotlib.pyplot as plot

def create_dataframe():
    with open('data/tiktok.json', 'r', encoding='utf-8') as file:
        data = json.loads(file.read())       
        file.close()
        video_history = data['Activity']['Video Browsing History']['VideoList']
        dataframe = pd.json_normalize(video_history)
        
        dataframe = dataframe.rename({'Date':'timestamp'}, axis='columns')
        dataframe['timestamp'] = pd.to_datetime( dataframe['timestamp'], format="%Y-%m-%d %H:%M:%S")
        dataframe['Date'] = dataframe['timestamp'].dt.date
        dataframe = dataframe.dropna()
         
        return dataframe

def set_hours(hour):
    hour = str(hour)
    if len(hour) == 1:
        hour = "0" + hour
    hour += ":00"
    return hour


def show_hours_views(data_frame):
    #data_frame = pd.DataFrame(data)
    #data_frame['timestamp'] = data_frame['timestamp'].apply(convert_time)
    
    #data_frame['timestamp'] = pd.to_datetime( data_frame['timestamp'], format='%d%b%Y %H:%M:%S')
    data_frame['timestamp'] = data_frame['timestamp'].dt.hour
    data_frame['timestamp'] = data_frame['timestamp'].apply(set_hours)
    
    data_frame = data_frame.groupby("timestamp").size().reset_index(name='count')
    data_frame.plot.bar(x="timestamp", y="count")
    plot.show(block=True)

if __name__ == '__main__':
    dataframe = create_dataframe()
    #show_hours_views(dataframe)
    print(dataframe.describe())
    df = dataframe.groupby('Date').size().reset_index(name='total_of_the_day')
    print(df['Date'].min())
    df.plot(x='Date', y='total_of_the_day')
    plot.show()