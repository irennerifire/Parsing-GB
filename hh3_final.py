from pymongo import MongoClient
from pprint import pprint
#from hh2_final import hh_parse
from bs4 import BeautifulSoup as bs
import requests
import re
import urllib

head = {'accept': '*/*',
          'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
          }
name = str(input('Введите название искомой вакансии (если название состоит из нескольких слов, вместо пробелов наберите знак "+"):    '))
page = str(input('Введите количество страниц, которые хотите проанализировать:    '))

url = 'https://spb.hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&search_period=3&text='+name+'&page='

def hh_parse(base_url, headers):
    vacancies = []
    session = requests.Session()
    req = session.get(base_url, headers = head)
    if req.status_code == 200:
        bscontent = bs(req.content, 'lxml')
        divs = bscontent.find_all('div', attrs = {'data-qa':'vacancy-serp__vacancy'})
        #print(len(divs))
        for div in divs:
            title = div.find('a', attrs = {'data-qa': 'vacancy-serp__vacancy-title'}).text
            href = div.find('a', attrs = {'data-qa': 'vacancy-serp__vacancy-title'})['href']
            site = urllib.parse.urlsplit(href).netloc
            if div.find('div', attrs = {'data-qa': 'vacancy-serp__vacancy-compensation'}) != None:
                sal = div.find('div', attrs = {'data-qa': 'vacancy-serp__vacancy-compensation'}).text
                sal = re.sub('[\\s]+', '', sal)
                val_list = ['руб', 'EUR', 'USD', 'RUB']
                val = re.findall(r"(?=("+'|'.join(val_list)+r"))", sal)
                if not val:
                    valute = 'None'
                else:
                    valute = val[0]
                p = re.compile('^(от|до)')
                pp = re.compile('^\d')
                d = re.compile('[\d]+')
                if pp.match(sal):
                    nums = re.findall(d, sal)
                    min_salary = nums[0]
                    max_salary = nums[1]
                    vacancies.append({
                        'title': title,
                        'link': href,
                        'site': site,
                        'minimal salary': float(min_salary),
                        'maximal salary': float(max_salary),
                        'valute': valute
                    })
                elif p.match(sal):
                    po = re.compile('^[от]')
                    pd = re.compile('^[до]')
                    fromf = po.match(sal)
                    upto = pd.match(sal)
                    if fromf:
                        digit = re.search(d, sal)
                        min_salary = sal[digit.start():digit.end()]
                        vacancies.append({
                            'title': title,
                            'link': href,
                            'site': site,
                            'maximal salary': 'unknown',
                            'minimal salary': float(min_salary),
                            'valute': valute
                        })
                    elif upto:
                        digit = re.search(d, sal)
                        max_salary = sal[digit.start():digit.end()]
                        vacancies.append({
                            'title': title,
                            'link': href,
                            'site': site,
                            'minimal salary': 'unknown',
                            'maximal salary': float(max_salary),
                            'valute': valute
                        })
            else:
                sal = 'unknown'
                vacancies.append({
                    'title': title,
                    'link': href,
                    'site': site,
                    'minimal salary': sal,
                    'maximal salary': sal,
                    'valute': 'None'
                })
    else:
        print('error')
    return vacancies

vac = []

for i in range(int(page)):
    base_url = url+str(i)
    print(base_url)
    vac.append(hh_parse(base_url, head))

#pprint(vac)
#print(type(vac))
#print(type(vac[0]))

client = MongoClient('localhost', 27017)

db = client['HeadHunter']

hh = db.HeadHunter

for el in vac:
    for j in el:
        hh.insert_one(j)

objects = hh.find()
for i in objects:
    pprint(i)

print('')
print('Вакансии с зарплатой > 50 000 руб')
print('')

r = hh.find({'minimal salary': {'$gt': 50000.0}}, {'_id', 'title', 'minimal salary'})
for i in r:
    pprint(i)
