from bs4 import BeautifulSoup
import json
import re

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251" 
    "]+"
)

def create_json_element(div):
        if len(div.find_all("a")) != 2:
                return None
        title, channel = [ a.text for a in div.find_all("a")]
        str_to_replace = [title, channel, "\n" ,"Hai guardato", "Haiguardato"]
        timestamp: str = div.text
        for str in str_to_replace:
                timestamp = timestamp.replace(str, "")
        timestamp.strip()
        #print(title, channel, timestamp)
        json_element = {
                "title": title,
                "channel": channel,
                "timestamp": " ".join(timestamp.split())
        }

        return json_element

def delete_emoji(text):
        return EMOJI_PATTERN.sub(r'', text)



                
if __name__ == "__main__":
        
        DIV_CLASS = 'content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1'
        #List to store all videos watched
        json_content = []
        

        with open("cronologiavisualizzazioni2.html", "r" ,encoding="utf8") as fp:
                file = delete_emoji("".join(fp.readlines()))
                print("EMOJIS DELETED!")
                soup = BeautifulSoup(file, "html.parser")
                #print(soup.head.title)
                divs = soup.find("body").find_all('div', attrs={'class': DIV_CLASS})
                
                for div in divs:
                        json_element = create_json_element(div)
                        if json_element:
                                json_content.append(json_element)

                with open("data2.json", "w") as fp_json:
                        fp_json.write(json.dumps(json_content))
                
                
                fp.close()
                fp_json.close()


