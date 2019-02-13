from django.contrib import admin
from .models import GameOfNewModel


class GameOfNewAdmin(admin.ModelAdmin):
    list_display = ('show_cover', 'title', 'release_date', 'price_option', 'price_full', 'discount_size')
    list_display_links = ('show_cover', 'title', )
    list_filter = ('release_date', 'price_option')
    search_fields = ('title', )
    fieldsets = (
        ('Основное', {'fields': ('title', 'steam_url', 'cover_url', 'release_date', )}),
        ('О цене', {'fields': ('price_full', 'price_discounted', 'discount_size', )}),
        ('Теги', {'fields': ('game_tags', )}),
    )


admin.site.register(GameOfNewModel, GameOfNewAdmin)
