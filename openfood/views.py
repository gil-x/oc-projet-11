from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.urls import reverse, reverse_lazy
from .models import Product, Category, Position
from .forms import SearchForm
from django.db.models import Q
import requests
import json

def get_products(request):
    """
    This view provides a JSON set of products of all grades but A.
    Used by jQuery autocomplete to suggests registered products.
    """
    if request.is_ajax():
        q = request.GET.get('term', '')
        print("x" + q + "x")
        products = Product.objects.filter(
            Q(product_name__istartswith = q) &
            (Q(grade='e') | Q(grade='d') | Q(grade='c') | Q(grade='b'))
            ).order_by('product_name')[:10]
        results = []
        
        for product in products:
            results.append(product.product_name)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def search_product(request):
    context = {}
    form = SearchForm(request.POST or None)
    context['form'] = form
    request.session["currentsearch"] = "search"
    context["currentsearch"] = request.session["currentsearch"]
    
    if form.is_valid(): 
        user_search = form.cleaned_data['search']
        context['search'] = user_search
        matching_products = Product.objects.filter(product_name__icontains=context['search'])

        if matching_products:
            context['result'] = matching_products[0]
            return HttpResponseRedirect(reverse(product_substitutes, kwargs={
                'pk': matching_products[0].pk,
                }))
        else:
            user_search = user_search.replace(" ", "-")
            return HttpResponseRedirect(reverse(search_on_off, kwargs={'search': user_search}))
    else:
        return render(request, 'openfood/index.html', context)


def search_on_off(request, search):
    context = {}
    context['user_search'] = search.replace("-", " ")

    url="https://fr.openfoodfacts.org/cgi/search.pl"

    args = {
            'action': "process",
            'search_terms': context['user_search'],
            'json': 1,
            'page_size': 10,
            }
    response = requests.get(url, params=args)
    products = []

    for product in response.json()["products"]:
        try:
            new_product = {}
            new_product['product_name'] = product['product_name']
            new_product['grade'] = product['nutrition_grades']
            new_product['barcode'] = product['code']
            new_product['categories'] = product['categories_hierarchy'][::-1]
            products.append(new_product)
        except KeyError:
            pass

    context['products'] = products

    return render(request, 'openfood/search_on_off.html', context)

def get_substitutes_on_off(request, barcode):
    # Instant search on OFF
    pass

    
def product_substitutes(request, pk):
    context = Product.objects.get_substitutes(pk)
    request.session["currentsearch"] = pk
    context["currentsearch"] = request.session["currentsearch"]
    return render(request, 'openfood/product_substitutes.html', context) # TODO Do not display products wich are already in user favorites ! (hard!)


def ramdom_product(request):
    context = {}
    product_e = Product.objects.filter(grade='e').order_by('?').first()
    context["product"] = product_e
    context = Product.objects.get_substitutes(product_e.pk)
    context["currentsearch"] = request.session["currentsearch"] = "random_{}".format(product_e.pk)
    return render(request, 'openfood/product_substitutes.html', context)


def product_detail(request, id):
    context = {}
    context["product"] = get_object_or_404(Product, pk=id)

    if request.user.is_authenticated:
         if context["product"] in request.user.profile.products.all():
            context["fav"] = True
    else:
        context["auth"] = False
    return render(request, 'openfood/product_detail.html', context)


def mentions(request):
    return render(request, 'openfood/mentions.html')
