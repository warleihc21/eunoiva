
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from autenticacao.views import index


urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('auth/', include('autenticacao.urls')),
    path('accounts/', include('allauth.urls')),
    path('noivos/', include('noivos.urls')),
    path('convidados/', include('convidados.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

