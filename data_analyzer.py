from abc import abstractmethod, ABC
from datetime import datetime
import json
import pandas as pd
import matplotlib.pyplot as plot

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

    #PARSE JSON AND CREATE A DATA FRAME OBJECT
    def create_dataframe(self):
        df = pd.DataFrame(self.load_data())
        df['timestamp'] = df['timestamp'].apply(self.convert_time)
        df['timestamp'] = pd.to_datetime( df['timestamp'], format='%d%b%Y %H:%M:%S', errors='coerce')
        df['Date'] = df['timestamp'].dt.date
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
    
    
        
class TikTokAnalyzer(DataAnalyzer):
    FILE_NAME = 'tiktok.json'
    def __init__(self, ) -> None:
        self.create_dataframe()
    
    def load_data(self):
        with open('data/tiktok.json', 'r', encoding='utf-8') as file:
            data = json.loads(file.read())       
            file.close()
            return data['Activity']['Video Browsing History']['VideoList']

    def create_dataframe(self):
        df = pd.json_normalize(self.load_data())
        df = df.rename({'Date':'timestamp'}, axis='columns')
        df['timestamp'] = pd.to_datetime( df['timestamp'], format="%Y-%m-%d %H:%M:%S")
        df['Date'] = df['timestamp'].dt.date
        df = df.dropna()
        self.data_frame = df






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
    yt = YoutubeAnalizer()
    tiktok = TikTokAnalyzer()
    # yt.show_barplot()
    # yt.show_hours_views()
    yt.show_video_by_day()
    #tiktok.show_hours_views()
    #tiktok.show_video_by_day()

    

        
    