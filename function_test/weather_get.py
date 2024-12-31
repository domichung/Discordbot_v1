import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
import datetime

url = 'https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization=CWB-BFCBB057-8F65-47C6-B171-C59BBF1E1999&format=JSON'
data = requests.get(url).json()
print('資料更新時間:'+data['cwaopendata']['sent'])
weather_data = data['cwaopendata']['dataset']['location']


def process_weather_data(data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Args:
        data: 原始天氣資料列表
    Returns:
        Dict: 依照時段整理的天氣資料
    """
    processed_data = {}
    
    for element in data:
        element_name = element['elementName']
        times = element['time']
        
        for time_slot in times:
            start_time = datetime.datetime.fromisoformat(time_slot['startTime'])
            start_time_str = start_time.strftime("%Y-%m-%d %H:%M")

            if start_time_str not in processed_data:
                processed_data[start_time_str] = {}
            
            parameter = time_slot['parameter']
            if element_name in ['MaxT', 'MinT']:
                value = f"{parameter['parameterName']}°{parameter['parameterUnit']}"
            elif element_name == 'PoP':
                value = f"{parameter['parameterName']}%"
            else:
                value = parameter['parameterName']
            
            processed_data[start_time_str][element_name] = value
    
    return processed_data


def display_weather_forecast(processed_data: Dict[str, Dict[str, str]],search_city) -> None:

    element_names = {
        'Wx': '天氣狀況',
        'MaxT': '最高溫度',
        'MinT': '最低溫度',
        'PoP': '降雨機率',
        'CI': '舒適度'
    }
    
    print("\n","-" * 40)
    print(f"天氣預報資訊({search_city})：")
    print("-" * 40)
    
    for time_slot, weather_data in sorted(processed_data.items()):
        print(f"\n時間：{time_slot}")
        print("-" * 40)
        for element, value in weather_data.items():
            print(f"{element_names.get(element, element)}: {value}")

def check_weather(_city):
    
    city_exist = 0
    
    for i in weather_data:
               
        if (_city != i['locationName']):
            continue
        else:
            new_weather_data = process_weather_data(i['weatherElement'])
            display_weather_forecast(new_weather_data,_city)
            city_exist = 1
             
        break
    
    if (city_exist == 0):
        return 'faild'
    
    else:
        return city_exist    
    
    
#print(check_weather('新竹縣'))
#print(data_jason)
check_weather('臺中市')