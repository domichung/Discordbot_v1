import requests
from bs4 import BeautifulSoup

def get_oil_price():
    
    url = "https://www.cpc.com.tw/GetOilPriceJson.aspx?type=TodayOilPriceString"
    
    response = requests.get(url)
    data = response.json()
    
    t_UpOrDown = data.get('UpOrDown_Html')
    if t_UpOrDown:
        soup = BeautifulSoup(t_UpOrDown, "html.parser")
        down_element = soup.find(class_="sys")
        rate_element = soup.find(class_="rate").find("i")

        if down_element and rate_element:
            down_text = down_element.get_text()
            rate_text = rate_element.get_text()
    
    t_PriceUpdate = data.get('PriceUpdate')

    result = (
        
        f"{t_PriceUpdate}零時起實施\n"
        f"本週油價{down_text}{rate_text}\n"
        f"92無鉛：{data.get('sPrice1')}元/公升\n"
        f"95無鉛：{data.get('sPrice2')}元/公升\n"
        f"98無鉛：{data.get('sPrice3')}元/公升\n"
        f"酒精汽油：{data.get('sPrice4')}元/公升\n"
        f"超級柴油：{data.get('sPrice5')}元/公升\n"
        f"液化石油氣：{data.get('sPrice6')}元/公升"
    )
    
    return result

#print(get_oil_price())