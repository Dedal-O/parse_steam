import requests
from bs4 import BeautifulSoup as bs
from time import sleep
from requests.exceptions import Timeout
from requests.exceptions import ProxyError, TooManyRedirects
from django.db import models
from django.utils.safestring import mark_safe
from taggit.managers import TaggableManager
from ..some_proxies.models import TheProxyModel


exp_list = (ProxyError, )


class GameOfNewModel(models.Model):
    PRICE_CHOICES = (
        ('free_to_play', 'Бесплатно'),
        ('demo', 'Демо'),
        ('full_price', 'по полной цене'),
        ('discounted', 'со скидкой'),
        ('not_defined', 'Не указана'),
    )
    title = models.CharField(verbose_name='Название', max_length=254)
    steam_url = models.URLField(verbose_name='Адрес в Steam', max_length=254)
    cover_url = models.URLField(verbose_name='Адрес обложки', max_length=254, blank=True, null=True)
    price_option = models.CharField(verbose_name='Тип цены', max_length=254, choices=PRICE_CHOICES, default='not_defined')
    price_full = models.FloatField(verbose_name='Цена полная, руб', default=0.0)
    price_discounted = models.FloatField(verbose_name='Цена со скидкой, руб', default=0.0)
    discount_size = models.PositiveSmallIntegerField(verbose_name='Размер скидки, %', default=0)
    release_date = models.DateField(verbose_name='Дата релиза', null=True, blank=True)
    game_tags = TaggableManager()

    def __str__(self):
        return f'{self.title}'

    def show_cover(self):
        if self.cover_url and self.cover_url != '':
            return mark_safe(f"<img src='{self.cover_url}'/>")
        else:
            return "(нет обложки)"

    def get_tags(self, session):
        while True:
            try:
                response = session.get(self.steam_url, timeout=15)
                break
            except Timeout:
                sleep(2)
                continue
            except exp_list:
                TheProxyModel.objects.all()[0].switch_next()
                the_proxy = TheProxyModel.objects.get(last_used=True)
                the_proxy.switch_next()
                the_proxy = TheProxyModel.objects.get(last_used=True)
                proxy_string = f"https://{the_proxy.login}:{the_proxy.password}@{the_proxy.ip}"
                session.proxies.update({'https': proxy_string})
                continue
            except TooManyRedirects:
                session = requests.Session()
                continue
        html_bs = bs(response.content, 'html.parser')
        app_tags = html_bs.find_all('a', {'class': 'app_tag'})
        if len(app_tags):
            game_tags = [tag.text.strip() for tag in app_tags]
#            last_comma = game_tags[:100].rfind(', ')
#            game_tags = game_tags[:last_comma]
            self.game_tags.set(*game_tags)
            self.save()
        return f"{self.id} - {self.title} - {game_tags}"

    class Meta:
        verbose_name = 'Игровая новинка'
        verbose_name_plural = 'Новинки игр'
