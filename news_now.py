import time
import random
import requests


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}


def get_news(num=10):
    print("reload now news")
    all_news = []
    pid = ''
    counter = 0
    while len(all_news) < 50:
        url = f'https://www.nownews.com/nn-client/api/v1/cat/breaking/?pid={pid}'
        r = requests.get(url, headers=HEADERS)
        if r.status_code != requests.codes.ok:
            print(f'Requests Error: {r.status_code}')
            break

        data = r.json()
        news_list = data['data']['newsList']
        for news in news_list:
            news_data = {
                'id': news['id'],
                'url': 'https://www.nownews.com' + news['postOnlyUrl'],
                'title': news['postTitle'],
                'content': news['postContent'],
                'date': news['newsDate']
            }
            
            news_entry = f"{counter+1}.{news['postTitle']}"
            all_news.append(news_entry)
            counter+=1
            if (counter > 19):
                return "\n".join(all_news)

        #pid = all_news[-1]['id']
        #time.sleep(random.uniform(2, 5))

    return "\n".join(all_news)

#print(get_news(20))