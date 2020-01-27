import requests
import json

username = 'irennerifire'

password = 'dragonfire54321'

response = requests.get('https://api.github.com/user/repos', auth=(username, password))

if response.ok:
    data = json.loads(response.text)
    for repo in data:
        print(repo['html_url'])
