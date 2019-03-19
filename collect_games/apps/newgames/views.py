import csv
from datetime import datetime
from logging import getLogger
import asyncio
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from taggit.models import Tag
from .models import GameOfNewModel, TaskCollectCheckModel
from .tasks import collect_the_games

logger = getLogger('newgames_logger')


def task_running(request):
    if TaskCollectCheckModel.objects.count == 0:
        TaskCollectCheckModel.objects.create()
    response = {'list_ready': TaskCollectCheckModel.objects.first().completed_flag, }
    return JsonResponse(response, safe=False)


def json_view(request):
    response = {
        'tags': [item['name'] for item in Tag.objects.all().values('name')],
    }
    json_games = []
    for game in GameOfNewModel.objects.order_by('release_date').all():
        if game.game_tags.count():
            json_games.append({
                "title": game.title,
                "game_url": game.steam_url,
                "game_cover": game.cover_url,
                "release_date": game.release_date,
                "price_full": game.price_full,
                "price_discounted": game.price_discounted,
                "discount_size": game.discount_size,
                "tags": [tag.name for tag in game.game_tags.order_by('name')]
            })
    response['games'] = json_games
    return JsonResponse(response, safe=False)


def csv_view(request):
    response = ''
    response += """Title, Game Url, Cover Url, Release Date, Price Full, Price Discounted,
                   Discount Size, Tags;"""
    for game in GameOfNewModel.objects.order_by('release_date').all():
        if game.game_tags.count():
            response += f"""{game.title}, {game.steam_url}, {game.cover_url}, {game.release_date}, {game.price_full}, {game.price_discounted}, {game.discount_size}, {'|'.join(tag.name for tag in game.game_tags.all())};"""
    return HttpResponse(response)


def csv_file_view(request):
    response = HttpResponse(content_type='text/csv')
    filename = f"newgames_{str(datetime.now())[:10].replace(' ', '_')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    csv_writer = csv.writer(response)
    csv_writer.writerow(['Title', 'game_url', 'cover_url', 'release_date', 'price_full', 'price_discounted',
                         'discount_size', 'tags'])
    for game in GameOfNewModel.objects.order_by('release_date').all():
        if game.game_tags.count():
            csv_writer.writerow([game.title, game.steam_url, game.cover_url, game.release_date, game.price_full,
                                 game.price_discounted, game.discount_size,
                                 '|'.join([tag.name for tag in game.game_tags.all()])])
    return response


class GamesVueView(TemplateView):
    template_name = 'newgames/index.html'

    def get_context_data(self, **kwargs):
        context = super(GamesVueView, self).get_context_data(**kwargs)
        return context


def renew_games_view(request):
    try:
        the_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(the_loop)
        future = asyncio.ensure_future(collect_the_games())
        the_loop.run_until_complete(future)
    except Exception:
        logger.info('running collect task errored')
    return redirect('/')
