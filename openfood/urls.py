from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^recherche/$', views.search_product, name='search_product'),
    url(r'^recherche-sur-off/(?P<search>[a-zA-Z0-9-]+)/$', views.search_on_off, name='search_on_off'),
    url(r'^un-produit-au-hasard/$', views.ramdom_product, name='ramdom_product'),
    url(r'^(?P<pk>\d+)/substituts/$', views.product_substitutes, name='product_substitutes'),
    url(r'^(?P<pk>\d+)/$', views.product_detail, name='product_view'),
]



