from django.contrib import admin
from .models import TheProxyModel


class TheProxyAdmin(admin.ModelAdmin):
    list_display = ('region', 'ip', 'login', 'password', 'last_used',)
    list_display_links = ('region', 'ip',)
    list_filter = ('last_used', 'region')
    search_fields = ('ip',)
    fields = ('ip', 'login', 'password', 'region')


admin.site.register(TheProxyModel, TheProxyAdmin)
