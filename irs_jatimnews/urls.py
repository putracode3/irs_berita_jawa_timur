"""irs_jatimnews URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-d views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.conf import settings
# from django.conf.urls.static import static

# from django.contrib import admin
# from django.conf.urls import include, url

# urlpatterns = [
#     url(r'^admin/', admin.site.urls),
#     url(r'^', include(('posts.urls', 'posts'), namespace='posts')),
# ]
# if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf.urls import url
from django.contrib import admin

from skripsi import views as aplikasi_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', aplikasi_views.masukkan),
    url(r'^simpan/', aplikasi_views.simpan),
    url(r'^preproses/', aplikasi_views.preproses),
    url(r'^term/', aplikasi_views.hitung_term),
    url(r'^manual/', aplikasi_views.manual_class),
]
