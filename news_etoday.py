import requests
from bs4 import BeautifulSoup

def loadnews(num):
    print("reload etoday news")
    newslist = "\n"
    counter = 0

    url = 'https://www.ettoday.net/news/realtime-hot.htm'
    web = requests.get(url)
    soup = BeautifulSoup(web.text, "html.parser")
    reservoir = soup.select('.piece')
    for i in reservoir:
        news = i.find('h3').get_text()   # 取得內容 h3 tag 的文字
        #print(news)
        newslist = newslist + str(counter+1) + "." + news + "\n"
        counter = counter + 1
        if (counter >= num):
            break
        
    #newslist = newslist + "\n資料來源 : https://www.ettoday.net/news/realtime-hot.htm"
    
    return newslist

#print(loadnews(20))