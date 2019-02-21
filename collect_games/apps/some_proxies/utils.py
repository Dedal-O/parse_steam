import re, requests
from bs4 import BeautifulSoup as bs
from django.conf import settings
from .models import TheProxyModel


def set_region(game_title_sample='sixcubes', cash_symbols='pуб', region='russia', only_empty=False):
    proxies_query = TheProxyModel.objects.filter(region=None) if only_empty else TheProxyModel.objects.all()
    proxies_worked = 0
    for proxy in proxies_query:
        try:
            response = requests.get(settings.PARSE_START_URL,
                                    proxies={'https': f"https://{proxy.login}:{proxy.password}@{proxy.ip}"}, timeout=15)
        except Exception:
            proxy.region = 'error'
            proxy.save()
            proxies_worked += 1
            continue
        if response.status_code != 200:
            proxy.region = 'error'
            proxy.save()
            proxies_worked += 1
            continue
        html_bs = bs(response.content, 'html.parser')
        for row in html_bs.find_all('a', attrs=re.compile('search_result_row.*')):
            if game_title_sample in row.find('span', {'class': 'title'}).text.lower():
                if cash_symbols in row.find('div', attrs=re.compile('.*search_price_discount_combined?.*')).text.lower():
                    proxy.region = region
                    proxy.save()
                    proxies_worked += 1
        return f"Изменено {proxies_worked} объектов"
