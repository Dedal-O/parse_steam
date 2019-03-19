from django.conf.urls import url
from .views import GamesVueView, csv_view, json_view, renew_games_view, task_running


urlpatterns = [
    url(r'^$', GamesVueView.as_view(), name='index'),
    url(r'^task_status$', task_running, name='task_running'),
    url(r'^list.csv$', csv_view),
    url(r'^list.json$', json_view),
    url(r'^renew_games$', renew_games_view, name='renew'),
]
