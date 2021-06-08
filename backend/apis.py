import requests
import os
from backend.utils import cyan

API_KEY = os.environ.get('CURRENCY_CONVERT_API_KEY')

def convert_currency_to_cop(currency):
    formula = f'{currency}_COP'
    url = f'https://free.currconv.com/api/v7/convert?q={formula}&compact=ultra&apiKey={API_KEY}'
    print(cyan(url), flush=True)
    request = requests.get(url)
    result = request.json()
    return result.get(f'{formula}')

