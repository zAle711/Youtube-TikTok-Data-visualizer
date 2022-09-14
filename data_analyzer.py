from abc import abstractmethod, ABC
from datetime import datetime
import json
import pandas as pd
import matplotlib.pyplot as plot
from matplotlib.animation import FuncAnimation, FFMpegWriter
from dateutil.relativedelta import relativedelta
import os
import sys

class DataAnalyzer(ABC):
    data_frame: pd.DataFrame = None
    def __init__(self) -> None:

        if not os.path.isdir('img'):
            os.mkdir('img')
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
    def show_views_by_hours(self):
        #Function to select 
        def set_hours(hour):
            if 'nan' != str(hour):
                hour = str(hour)
                hour.replace('.', ':')
                hour = '0' + hour + '0' if len(hour) == 3 else hour + '0'
                return hour

        df = self.data_frame.copy()
        df['timestamp'] = df['timestamp'].dt.hour
        df['timestamp'] = df['timestamp'].apply(set_hours)
        
        df = df.groupby("timestamp").size().reset_index(name='count')
        df.plot.bar(x="timestamp", y="count", title="Most Viewed Channels", fontsize=10)
        plot.tight_layout()
        plot.savefig(self.get_file_name('views_by_hours'))
        #plot.show(block=True)
    
    #PLOT Total of video watched every day
    def show_views_by_day(self):
        #Count video watched every day
        df = self.data_frame.groupby('date').size().reset_index(name='total_of_the_day')

        #Add rows with empty days with 0 as total videos watched
        dtr = pd.date_range(df['date'].min(), df['date'].max(), freq='D').to_frame(name='date')
        dtr['total_of_the_day'] = 0

        df.merge(dtr, how='right', on='date').fillna(0).pop('total_of_the_day_y')

        
        
        df.plot(x='date', y='total_of_the_day')
        plot.tight_layout()
        plot.savefig(self.get_file_name('views_by_day_alltime.png'))
    
    @abstractmethod
    def get_file_name(self, name):
        pass

    @abstractmethod
    def to_csv(self):
        pass

class YoutubeAnalizer(DataAnalyzer):
    FILE_NAME = 'youtube.json'
    def __init__(self) -> None:
        super().__init__()
        self.create_dataframe()

    def load_data(self):
        if not os.path.isfile('data/youtube.json'):
            print("Place your youtube.json in a folder named: data")
            sys.exit(0)
        with open(f"data/{self.FILE_NAME}", "r", encoding="utf-8") as fp:
            file_content = fp.read()
            fp.close()
            return json.loads(file_content)

    def to_csv(self):
        self.data_frame.to_csv(f"data/{self.FILE_NAME[:-5]}.csv")

    
    #PARSE JSON AND CREATE A DATA FRAME OBJECT
    def create_dataframe(self):

        #translate italian months to english needed to convert timestamp to pd.DateTime    
        def convert_time(timestamp:str):
        
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
        
        df = pd.DataFrame(self.load_data())
        df['timestamp'] = df['timestamp'].apply(convert_time)
        df['timestamp'] = pd.to_datetime( df['timestamp'], format='%d%b%Y %H:%M:%S', errors='coerce')
        df['date'] = pd.to_datetime( df['timestamp'].dt.date, format='%Y-%m-%d')
        self.data_frame = df
    

    #BAR PLOT OF THE MOST VIEWED CHANNELS
    def show_barplot(self):

        df = self.data_frame.groupby('channel')['channel'].count().reset_index(name='views')
        df = df[df['views'] > 20]
        df = df.sort_values('views', ascending=False)
        df.head(20).plot.barh(x="channel", y="views", title="Most Viewed Channels", fontsize=10)
        plot.ylabel('Channel name', fontdict={'fontsize':15}, fontsize=15)
        plot.tight_layout()
        plot.savefig(self.get_file_name('most_viewed_channel'))
        #plot.show(block=True)
    
    #PLOT ANIMATION OF THE MOST VIEWED CHANNEL EVERY MOUNT (CUMULATIVE)
    def animated_plot(self): 

        def filter_data(df):
            all_data = []
            all_time = []
            start = datetime(2013, 4, 10)
            end = self.data_frame['date'].max()

            while start <= end:
                all_time.append(start)
                query = df[ df['date'] < start ].groupby('channel')['channel'].count().reset_index(name='total').sort_values('total', ascending=False).head(20)
                all_data.append(query)
                start = start + relativedelta(months=1)

            return all_data, all_time
        
        def get_data(n):
            return all_df[n]

        all_df, all_time = filter_data(self.data_frame)

        fig = plot.figure(figsize=(10,5))
        first_data = get_data(0)
        plot.barh(first_data['channel'], first_data['total'])
        plot.tight_layout()
        
        def animate(i):
            plot.cla()
            next_data = all_df[i]
            plot.gca().barh(next_data['channel'], next_data['total'])
            plot.tight_layout()
            plot.suptitle(all_time[i].strftime("%Y-%m-%d"), fontsize=20)
        
        animation = FuncAnimation(fig, animate, frames=len(all_df), repeat=False, interval=200)
        FFwriter = FFMpegWriter(fps=4)
        animation.save('img/most_wieved_channels.mp4', writer=FFwriter)
        
        

    def get_file_name(self, name):
        return f"img/yt_{name}.png"


class TikTokAnalyzer(DataAnalyzer):
    FILE_NAME = 'tiktok.json'
    def __init__(self, ) -> None:
        self.create_dataframe()
    
    def load_data(self):
        if not os.path.isfile('data/tiktok.json'):
            print("Place your tiktok.json in a folder named: data")
            sys.exit(0)
        with open('data/tiktok.json', 'r', encoding='utf-8') as file:
            data = json.loads(file.read())       
            file.close()
            return data['Activity']['Video Browsing History']['VideoList']
    
    def to_csv(self):
        self.data_frame.to_csv(f"data/{self.FILE_NAME[:-5]}.csv")

    def create_dataframe(self):
        df = pd.json_normalize(self.load_data())
        df = df.rename({'Date':'timestamp'}, axis='columns')
        df['timestamp'] = pd.to_datetime( df['timestamp'], format="%Y-%m-%d %H:%M:%S")
        df['date'] = pd.to_datetime( df['timestamp'].dt.date, format='%Y-%m-%d')
        df = df.dropna()
        self.data_frame = df

    def get_file_name(self, name):
        return f"img/{name}.png"

if __name__ == "__main__":
    yt = YoutubeAnalizer()    
    tiktok = TikTokAnalyzer()
    
    tiktok.show_views_by_hours()
    tiktok.show_views_by_day()

    yt.show_barplot()
    yt.show_views_by_hours()
    yt.show_views_by_day()    
    yt.animated_plot()

    yt.to_csv()
    tiktok.to_csv()