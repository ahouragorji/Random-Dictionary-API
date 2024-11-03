import requests


def getRandomWord():      
    api_url = 'https://api.api-ninjas.com/v1/randomword'
    response = requests.get(api_url, headers={'X-Api-Key': 'xgWcOYg9f1r6/gE9tDIR+Q==ZqL1oPWeOeKMSQwp'})
    if response.status_code == requests.codes.ok:
        return response.text
    else:
       return None
def getMeaning(word):
    api_url = 'https://api.api-ninjas.com/v1/dictionary?word={}'.format(word)
    response = requests.get(api_url, headers={'X-Api-Key': 'xgWcOYg9f1r6/gE9tDIR+Q==ZqL1oPWeOeKMSQwp'})
    if response.status_code == requests.codes.ok:
        return response.text
    else:
        return None
        