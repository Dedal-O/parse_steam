import re, requests, logging
from bs4 import BeautifulSoup as bs
from requests.exceptions import Timeout
from datetime import datetime, date, timedelta
from time import sleep, strptime
from django.conf import settings
from carrot.utilities import publish_message
from ..some_proxies.models import TheProxyModel
from .models import GameOfNewModel, exp_list

release_date_pass_list = ('com', 'ear', 'ann', )
logger = logging.getLogger('newgames_logger')


def collect_the_games():
    start_moment = datetime.now()
    GameOfNewModel.objects.filter(release_date__lte=(datetime.now() - timedelta(days=14))).delete()
    logger.info(f"{datetime.now()} - Начало работы сбора новинок")
    the_session = requests.Session()
    the_session.cookies.set('wants_mature_content', '1')
    TheProxyModel.objects.all()[0].switch_next()
    the_proxy = TheProxyModel.objects.get(last_used=True)
    proxy_string = f"https://{the_proxy.login}:{the_proxy.password}@{the_proxy.ip}"
    the_session.proxies.update({'https': proxy_string})
    while True:
        try:
            response = the_session.get(settings.PARSE_START_URL, timeout=15)
            break
        except Timeout:
            sleep(2)
            continue
        except exp_list:
            the_proxy.switch_next()
            the_proxy = TheProxyModel.objects.get(last_used=True)
            proxy_string = f"https://{the_proxy.login}:{the_proxy.password}@{the_proxy.ip}"
            the_session.proxies.update({'https': proxy_string})
            continue
    html_bs = bs(response.content, 'html.parser')
    page_count_links = html_bs.find_all("a", href=re.compile(r".*&page=?.*"))
    pages_href = page_count_links[-2]
    try:
        last_page = int(pages_href.text)
    except Exception:
        last_page = 1
    logger.info(f"{datetime.now()} - Последняя страница в списке - {last_page}")
    game_structs = []
    items_worked = 0
    flag_old_game = False
    for page in range(1, last_page+1):
        if flag_old_game:
            break
        while True:
            try:
                response = the_session.get(f"{settings.PARSE_START_URL}&page={page}", timeout=15)
                break
            except Timeout:
                sleep(2)
                continue
            except exp_list:
                the_proxy.switch_next()
                the_proxy = TheProxyModel.objects.get(last_used=True)
                proxy_string = f"https://{the_proxy.login}:{the_proxy.password}@{the_proxy.ip}"
                the_session.proxies.update({'https': proxy_string})
                continue
        page_html_bs = bs(response.content, 'html.parser')
        for row_item in page_html_bs.find_all("a", attrs=re.compile(".*search_result_row?.*")):
            if 'ds_excluded_by_preferences' in row_item.attrs['class']:
                # Найдена скрытая игра, пропускаем
                continue
            release_date_steam = row_item.find('div', attrs=re.compile(".*search_released?.*")).text
            release_date = release_date_steam.replace(',', '').split(' ')
            if len(release_date) and release_date[0] is not '' and not \
                any(pass_string in release_date_steam.lower() for pass_string in release_date_pass_list):
                if len(release_date) < 3:
                    if 'winter' in release_date_steam:
                        the_mon = datetime.now().strftime('%B') if datetime.now().month in (1, 2, 12) else 'dec'
                        release_date = ['1', the_mon, release_date_steam.split(' ')[-1]]
                    elif 'spring' in release_date_steam:
                        release_date = ['1', 'mar', release_date_steam.split(' ')[-1]]
                    elif 'summer' in release_date_steam:
                        release_date = ['1', 'jun', release_date_steam.split(' ')[-1]]
                    elif 'autumn' in release_date_steam:
                        release_date = ['1', 'sep', release_date_steam.split(' ')[-1]]
                    elif len(release_date) < 2:
                        if not release_date[-1].isdigit():
                            continue
                        else:
                            if len(release_date[0]) == 4:
                                release_date.append('jan')
                                release_date.append(release_date[0])
                                release_date[0] = 1
                            else:
                                continue
                    else:
                        release_date.append(release_date[1])
                        release_date[1] = release_date[0]
                        release_date[0] = 28
                elif 'release' in release_date_steam.lower():
                    if any(char.isdigit() for char in release_date[2]):
                        release_date[0] = release_date[2]
                    else:
                        release_date[0], release_date[1] = release_date[1], release_date[2]
                    release_date[2] = release_date[3]
                elif not any(char.isdigit() for char in release_date[0]):
                    release_date[0], release_date[1] = release_date[1], release_date[0]
                release_date[0] = int(release_date[0])
                release_date[1] = int(strptime(release_date[1][:3], '%b').tm_mon)
                release_date[2] = int(release_date[2])
                release_date_actual = date(year=release_date[2], month=release_date[1], day=release_date[0], )
                if release_date_actual is not None:
                    if datetime.combine(release_date_actual, datetime.min.time()) < (datetime.now() - timedelta(days=14)):
                        logger.info(f"""{datetime.now()} - Найдена достаточно старая игра с датой {release_date_actual},
                                        обход завершается.
                                        Найдено новых игр {len(game_structs)}""")
                        flag_old_game = True
                    item_struct = {
                     'title': row_item.find_all('span', attrs=re.compile('.*title?.*'))[0].text,
                     'game_url': row_item.get('href')[:row_item.get('href').rfind('/?')],
                     'img_url': row_item.find('img').get('src'),
                     'prices_block': row_item.find_all('div', attrs=re.compile('.*search_price_discount_combined?.*')),
                     'release_date_actual': release_date_actual,
                    }
                    game_structs.append(item_struct)
    logger.info(f"{datetime.now()} - Завершён обход основного списка. Собрано {len(game_structs)} записей.")
    for item_struct in game_structs:
        game, created = GameOfNewModel.objects.get_or_create(steam_url=item_struct['game_url'])
        game.title = item_struct['title']
        game.cover_url = item_struct['img_url']
        game.release_date = item_struct['release_date_actual']
        prices_bs = item_struct['prices_block']
        if 'free' in prices_bs[0].text.lower():
            game.price_option = 'free_to_play'
        elif 'demo' in prices_bs[0].text.lower():
            game.price_option = 'demo'
        elif len(prices_bs[0].find_all('div', attrs=re.compile('.*search_discount?.*'))):
            discount_text = prices_bs[0].find('div', attrs=re.compile('.*search_discount?.*')).text.strip()
            if len(discount_text) > 1:
                prices_texts = prices_bs[0].find('div', attrs=re.compile('.*search_price?.*discounted?.*')).text.strip().replace(',', '.').split('pуб.')
#                logger.info(f"{item_struct['title']}, discount text {discount_text}, prices text {prices_texts}")
                game.discount_size = int(re.sub(r'\D+', '', discount_text))
                game.price_discounted = float(prices_texts[1])
                game.price_full = float(prices_texts[0])
                game.price_option = 'discounted'
            else:
                price_full_text = prices_bs[0].find('div', attrs=re.compile('.*search_price?.*')).text.strip().replace(',', '.').replace(' pуб.', '')
                if any(char.isdigit() for char in price_full_text):
                    game.price_full = float(price_full_text)
                    game.price_option = 'full_price'
                else:
                    game.price_option = 'not_defined'
        game.save()
        logger.info(f"{datetime.now()} - getting tags for {game.steam_url}")
        tags_result = game.get_tags(session=the_session)
        logger.info(f"{datetime.now()} - {tags_result}")

    the_session.close()
    ret_message = f"{datetime.now()} - Задача завершена. Затрачено времени {datetime.now() - start_moment}"
    logger.info(ret_message)
    return ret_message


publish_message(collect_the_games, )
