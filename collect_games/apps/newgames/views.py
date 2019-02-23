import csv
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from .models import GameOfNewModel


def json_view(request):
    response = []
    for game in GameOfNewModel.objects.order_by('release_date').all():
        if game.game_tags.count():
            response.append({
                "title": game.title,
                "game_url": game.steam_url,
                "game_cover": game.cover_url,
                "release_date": game.release_date,
                "price_full": game.price_full,
                "price_discounted": game.price_discounted,
                "discount_size": game.discount_size,
                "tags": [tag.name for tag in game.game_tags.all()]
            })
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
