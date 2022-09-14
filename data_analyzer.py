from abc import abstractmethod, ABC
from timeit import repeat
from turtle import update, width
import numpy as np
from datetime import datetime
import json
import pandas as pd
import matplotlib.pyplot as plot
from matplotlib.animation import ArtistAnimation, FuncAnimation, FFMpegWriter
from dateutil.relativedelta import relativedelta
class DataAnalyzer(ABC):
    data_frame = None
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def load_data(self):
        pass
    @abstractmethod
    def create_dataframe(self):
        pass

    def get_dataframe(self):
        if not self.data_frame:
            self.create_dataframe()
        return self.data_frame
    
    #PLOT NUMBERS OF VIDEO SAW BY TIME OF THE DAY (every hour)
    def show_hours_views(self):
        #Function to select 
        def set_hours(hour):
            hour = str(hour)
            if len(hour) == 1:
                hour = "0" + hour
            hour += ":00"
            return hour

        df = self.data_frame.copy()
        df['timestamp'] = df['timestamp'].dt.hour
        df['timestamp'] = df['timestamp'].apply(set_hours)
        
        df = df.groupby("timestamp").size().reset_index(name='count')
        df.plot.bar(x="timestamp", y="count")
        plot.show(block=True)
    
    #PLOT Total of video watched every day
    def show_video_by_day(self):
        df = self.data_frame.groupby('Date').size().reset_index(name='total_of_the_day')
        df[ df['Date'] > datetime(2021,1,1,0,0,0).date() ].plot(x='Date', y='total_of_the_day')
        plot.show()
    
    @abstractmethod
    def to_csv(self):
        pass

class YoutubeAnalizer(DataAnalyzer):
    FILE_NAME = 'youtube.json'
    def __init__(self) -> None:
        super().__init__()
        self.create_dataframe()

    def load_data(self):
        with open(f"data/{self.FILE_NAME}", "r", encoding="utf-8") as fp:
            file_content = fp.read()
            fp.close()
            return json.loads(file_content)

    def to_csv(self):
        self.data_frame.to_csv(f"{self.FILE_NAME[:-5]}.csv")
    #PARSE JSON AND CREATE A DATA FRAME OBJECT
    def create_dataframe(self):
        df = pd.DataFrame(self.load_data())
        df['timestamp'] = df['timestamp'].apply(self.convert_time)
        df['timestamp'] = pd.to_datetime( df['timestamp'], format='%d%b%Y %H:%M:%S', errors='coerce')
        df['date'] = pd.to_datetime( df['timestamp'].dt.date, format='%Y-%m-%d')
        #df['Date'] = df['timestamp'].dt.date
        self.data_frame = df
    
    #translate italian months to english needed to convert timestamp to pd.DateTime    
    def convert_time(self, timestamp:str):
        
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

    #BAR PLOT OF THE MOST VIEWED CHANNELS
    def show_barplot(self):

        df = self.data_frame.groupby('channel')['channel'].count().reset_index(name='views')
        df = df[df['views'] > 20]
        df = df.sort_values('views', ascending=False)
        df.head(20).plot.bar(x="channel", y="views", title="Most Viewed Channels", figsize=(50, 50))
        plot.subplots_adjust(bottom=.3)
        plot.show(block=True)
    
    def animated_plot(self): 

        def filter_data(df):
            all_data = []
            start = datetime(2013, 4, 10)
            end = self.data_frame['date'].max()

            while start <= end:
                print(start)
                query = df[ df['date'] < start ].groupby('channel')['channel'].count().reset_index(name='total').sort_values('total', ascending=False).head(20)
                all_data.append(query)
                start = start + relativedelta(months=1)

            return all_data
        

        
        def get_data(n):
            return all_df[n]

        all_df = filter_data(self.data_frame)
        print(all_df[50])

        fig = plot.figure()
        first_data = get_data(0)
        plot.barh(first_data['channel'], first_data['total'])
        
        def animate(i):
            if i == len(all_df):
                return
            plot.cla()
            next_data = get_data(i)
            plot.gca().barh(next_data['channel'], next_data['total'])
        
        animation = FuncAnimation(fig, animate, frames=len(all_df), repeat=False, interval=100)
        FFwriter = FFMpegWriter(fps=30)
        animation.save('test.mp4', writer=FFwriter)
        
        plot.show()


class TikTokAnalyzer(DataAnalyzer):
    FILE_NAME = 'tiktok.json'
    def __init__(self, ) -> None:
        self.create_dataframe()
    
    def load_data(self):
        with open('data/tiktok.json', 'r', encoding='utf-8') as file:
            data = json.loads(file.read())       
            file.close()
            return data['Activity']['Video Browsing History']['VideoList']
    
    def to_csv(self):
        self.data_frame.to_csv(f"{self.FILE_NAME[:-5]}.csv")

    def create_dataframe(self):
        df = pd.json_normalize(self.load_data())
        df = df.rename({'Date':'timestamp'}, axis='columns')
        df['timestamp'] = pd.to_datetime( df['timestamp'], format="%Y-%m-%d %H:%M:%S")
        df['date'] = pd.to_datetime( df['timestamp'].dt.date, format='%Y-%m-%d')
        df = df.dropna()
        self.data_frame = df


if __name__ == "__main__":
    yt = YoutubeAnalizer()
    yt.to_csv()
    tiktok = TikTokAnalyzer()
    # yt.show_barplot()
    # yt.show_hours_views()
    #yt.show_video_by_day()
    #tiktok.show_hours_views()
    #tiktok.show_video_by_day()
    yt.animated_plot()

    

        
    