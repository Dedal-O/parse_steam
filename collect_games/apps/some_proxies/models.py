import logging
from django.db import models
logger = logging.getLogger('newgames_logger')


class TheProxyModel(models.Model):
    REGION_CHOICES = (
        ('russia', 'Россия'),
        ('europe', 'Европа'),
        ('uk', 'Великобритания'),
        ('usa', 'США'),
        ('error', 'Ошибка'),
        (None, 'не указан'),
    )
    ip = models.CharField(verbose_name='ip', max_length=254)
    login = models.CharField(verbose_name='login', max_length=254)
    password = models.CharField(verbose_name='password', max_length=254)
    region = models.CharField(verbose_name='Регион', max_length=254, choices=REGION_CHOICES, blank=True, null=True)
    last_used = models.BooleanField(verbose_name='Last used flag', default=False)

    def __str__(self):
        return f'https://{self.login}:{self.password}@{self.ip}'

    def switch_next(self, region='russia'):
        id_s = type(self).objects.filter(region=region).order_by('id').values('id')
        if type(self).objects.filter(last_used=True).count():
            the_index = type(self).objects.filter(last_used=True)[0].id
        else:
            the_index = id_s.first()['id']
        type(self).objects.all().update(last_used=False)
        if the_index == id_s.last()['id']:
            the_index = id_s[0]['id']
        else:
            for the_i in range(0, len(id_s)):
                if id_s[the_i]['id'] == the_index:
                    the_index = id_s[the_i+1]['id']
                    break
#        logger.info(f"getting proxy with index {the_index}")
        the_proxy = type(self).objects.get(id=the_index)
        the_proxy.last_used = True
        the_proxy.save()

    class Meta:
        verbose_name = 'Прокси'
        verbose_name_plural = 'Прокси'


def NextProxy(region='russia', http=False):
    TheProxyModel.objects.all()[0].switch_next(region=region)
    the_proxy = TheProxyModel.objects.get(last_used=True)
    return f"{'http' if http else 'https'}://{the_proxy.login}:{the_proxy.password}@{the_proxy.ip}"
