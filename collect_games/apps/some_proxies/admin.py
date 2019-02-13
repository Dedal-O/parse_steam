from django.contrib import admin
from .models import TheProxyModel


class TheProxyAdmin(admin.ModelAdmin):
    list_display = ('ip', 'login', 'password', 'last_used',)
    list_display_links = ('ip',)
    list_filter = ('last_used',)
    search_fields = ('ip',)
    fields = ('ip', 'login', 'password')


admin.site.register(TheProxyModel, TheProxyAdmin)
