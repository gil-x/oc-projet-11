"""pur_beurre URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
# from django.views.generic import TemplateView

from openfood import views as openfood_views
from openuser import views as openuser_views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^$', openfood_views.search_product, name='search_product'),
    url(r'^produits/', include('openfood.urls')),
    url(r'^api/get_products/', openfood_views.get_products, name='get_products'),
    url(r'^inscription/', openuser_views.registration, name='registration'),
    url(r'^connexion/', openuser_views.log_in, name='log_in'),
    url(r'^deconnexion/', openuser_views.log_out, name='log_out'),
    url(r'^admin/', admin.site.urls),
    url(r'^mon-espace/', include('openuser.urls')),
    url(r'^mentions-légales/', openfood_views.mentions, name='mentions'),

    url(r'^signup/$', openuser_views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        openuser_views.activate, name='activate'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
