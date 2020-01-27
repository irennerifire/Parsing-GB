#access_token=e92833b699f49a4e03d3f013ec7596963e7069359bd4dc5492a039b094e75067d742c2195afd5f32331a2   &   expires_in=86400    &    user_id=134347125
from pprint import pprint
import requests
import json

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
# main_link = 'https://www.google.com'
# response = requests.get(main_link,headers=headers)
main_link = 'https://api.openweathermap.org/data/2.5/weather'
# city='tommot'
# appid = 'e5e4cd692a72b0b66ea0a6b80255d1c3'
# link = f'{main_link}?q={city}&appid={appid}'
params={'q':'tommot',
        'appid':'e5e4cd692a72b0b66ea0a6b80255d1c3'}

response = requests.get(main_link,params=params)

if response.ok:
    time.sleep(1)
    data = json.loads(response.text)
    # pprint(data)
    # print(type(data))
    print(f"В городе {data['name']} температура {data['main']['temp'] - 273.15} градусов")
