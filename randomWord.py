import requests
import os
api_key1 = os.getenv('api_key1') # added these two
api_key2 =  os.getenv('api_key2')

def getRandomWord():      
    api_url = 'https://api.api-ninjas.com/v1/randomword'
    response = requests.get(api_url, headers={'X-Api-Key': api_key1})
    #response = requests.get(api_url, headers={'X-Api-Key': 'xgWcOYg9f1r6/gE9tDIR+Q==ZqL1oPWeOeKMSQwp'})
    if response.status_code == requests.codes.ok:
        return response.text
    else:
       return None
def getMeaning(word):
    api_url = 'https://api.api-ninjas.com/v1/dictionary?word={}'.format(word)
    response = requests.get(api_url, headers={'X-Api-Key': 'xgWcOYg9f1r6/gE9tDIR+Q==ZqL1oPWeOeKMSQwp'})
    #response = requests.get(api_url, headers={'X-Api-Key': 'xgWcOYg9f1r6/gE9tDIR+Q==ZqL1oPWeOeKMSQwp'})
    if response.status_code == requests.codes.ok:
        return response.text
    else:
        return None
        