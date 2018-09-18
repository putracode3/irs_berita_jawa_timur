from django.contrib import admin
from skripsi.models import *

# Register your models here.


class CrawlNewsAdmin(admin.ModelAdmin):
    list_display = ['headline', 'date', 'main_headline', 'content', 'url']
    list_filter = ('headline', 'date', 'main_headline', 'content', 'url')
    search_fields = ['headline', 'date', 'main_headline', 'content', 'url']
    list_per_page = 25


admin.site.register(CrawlNews, CrawlNewsAdmin)
