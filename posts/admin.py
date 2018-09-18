from django.contrib import admin
from .models import Post

# Register your models here.
class PostAdmin(admin.ModelAdmin):
  list_display = ['title','slug','image','content','timestamp','updated']
  list_filter = ['updated','timestamp']
  list_editable = ['title']
  prepopulated_fields = {'slug':('title',)}
  list_display_links = None

admin.site.register(Post, PostAdmin)
