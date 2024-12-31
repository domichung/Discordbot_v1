import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
import datetime

url = 'https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization={用戶金鑰}&format=JSON'
data = requests.get(url).json()
#print('資料更新時間:'+data['cwaopendata']['sent'])
weather_data = data['cwaopendata']['dataset']['location']


def process_weather_data(data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
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

def check_weather(_city):
    
    city_exist = 0
    
    for i in weather_data:
               
        if (_city != i['locationName']):
            continue
        else:
            new_weather_data = process_weather_data(i['weatherElement'])
            city_exist = 1
            break
             
    
    if (city_exist == 0):
        return 'faild'
    
    else:
        return new_weather_data,data['cwaopendata']['sent']
    
    
#print(check_weather('新竹縣'))
#print(data_jason)
#check_weather('臺中市')