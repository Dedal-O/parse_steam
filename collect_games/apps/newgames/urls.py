from .views import csv_view, json_view
from django.conf.urls import url
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='newgames/index.html'), name='index'),
    url(r'^list.csv$', csv_view),
    url(r'^list.json$', json_view),
]
