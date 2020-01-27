from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
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
            vacancies.append({
                'title': title,
                'link': href,
                'site': site
            })
            if div.find('div', attrs = {'data-qa': 'vacancy-serp__vacancy-compensation'}) != None:
                sal = div.find('div', attrs = {'data-qa': 'vacancy-serp__vacancy-compensation'}).text
                sal = re.sub('[\\s]+', '', sal)
                #print(sal)
                val_list = ['руб', 'EUR', 'USD', 'RUB']
                val = re.findall(r"(?=("+'|'.join(val_list)+r"))", sal)
                if not val:
                    vacancies.append({'valute': 'None'})
                else:
                    vacancies.append({'valute': val[0]})
                #re.sub('[\\ха]+', '', salary)
                p = re.compile('^(от|до)')
                pp = re.compile('^\d')
                d = re.compile('[\d]+')
                if pp.match(sal):
                    nums = re.findall(d, sal)
                    min_salary = nums[0]
                    max_salary = nums[1]
                    vacancies.append({
                        'minimal salary': min_salary,
                        'maximal salary': max_salary,
                        #'valute': val[0]
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
                            'maximal salary': 'unknown',
                            'minimal salary': min_salary,
                            #'valute': val[0]
                        })
                    elif upto:
                        digit = re.search(d, sal)
                        max_salary = sal[digit.start():digit.end()]
                        vacancies.append({
                            'minimal salary': 'unknown',
                            'maximal salary': max_salary,
                            #'valute': val[0]
                        })
                # разделитель в больших числах  /\d{1,3}(?=(\d{3})+(?!\d))/g
            else:
                sal = 'unknown'
                vacancies.append({
                    'minimal salary': sal,
                    'maximal salary': sal,
                    #'valute': 'None'
                })

            #pprint(vacancies)
    else:
        print('error')
    return vacancies

vac = dict()

for i in range(int(page)):
    base_url = url+str(i)
    print(base_url)
    key = 'page'+str(i)
    vac[key] = hh_parse(base_url, head)
    #vac = hh_parse(base_url, head)
    #pprint(vac)
    #pprint('   ')

pprint(vac)
