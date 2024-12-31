import requests
from bs4 import BeautifulSoup

def loadnews(num):
    print("reload yahoo news")
    newslist = []
    counter = 0

    url = 'https://tw.news.yahoo.com/'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = soup.find_all('h3', class_='Mb(5px)')
        
        for item in news_items:
            if counter >= num:
                break
                
            link = item.find('a')
            if link:
                title = link.text.strip()
                url = link.get('href')
                if url and not url.startswith('http'):
                    url = 'https://tw.news.yahoo.com' + url
                
                news_entry = f"{counter+1}.{title}"
                newslist.append(news_entry)
                counter += 1

        return "\n".join(newslist)
            
    except requests.RequestException as e:
        print(f"Error fetching news: {e}")
        return "Error fetching news"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred"

#print(loadnews(20))