import logging
from django.db import models
logger = logging.getLogger('newgames_logger')


class TheProxyModel(models.Model):
    ip = models.CharField(verbose_name='ip', max_length=254)
    login = models.CharField(verbose_name='login', max_length=254)
    password = models.CharField(verbose_name='password', max_length=254)
    last_used = models.BooleanField(verbose_name='Last used flag', default=False)

    def __str__(self):
        return f'https://{self.login}:{self.password}@{self.ip}'

    def switch_next(self):
        id_s = type(self).objects.order_by('id').values('id')
        if type(self).objects.filter(last_used=True).count():
            the_index = type(self).objects.filter(last_used=True)[0].id
        else:
            the_index = id_s.first()['id']
        type(self).objects.all().update(last_used=False)
        if the_index == id_s.last()['id']:
            the_index = id_s[0]['id']
        else:
            for the_i in range(0, len(id_s)-1):
                if id_s[the_i]['id'] == the_index:
                    the_index = id_s[the_i+1]['id']
                    break
        logger.info(f"getting proxy with index {the_index}")
        the_proxy = type(self).objects.get(id=the_index)
        the_proxy.last_used = True
        the_proxy.save()

    class Meta:
        verbose_name = 'Прокси'
        verbose_name_plural = 'Прокси'
