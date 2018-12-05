from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile
from openfood.models import Product
from .forms import CreateUser, LoginForm, SignupForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist

import json

def registration(request):
    context = {}

    if "currentsearch" in request.session:
        context["currentsearch"] = request.session["currentsearch"]
    else:
        context["currentsearch"] = "logout"

    if request.method == 'POST':
        context["form"] = SignupForm(request.POST)
        if context["form"].is_valid():
            user = context["form"].save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activez votre compte sur Pur Beurre'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = context["form"].cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'openuser/confirmation.html')
    else:
        context["form"] = SignupForm()
    return render(request, 'registration.html', context)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        new_profile = Profile()
        new_profile.user = user
        new_profile.save()
        login(request, user)
        return render(request, 'openuser/activation_success.html', {})
    else:
        return render(request, 'openuser/activation_fail.html', {})


def log_in(request):
    context = {}
    if "currentsearch" in request.session:
        context["currentsearch"] = request.session["currentsearch"]
    else:
        context["currentsearch"] = "logout"
    context["form"] = form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if request.method == 'GET' and 'next' in request.GET:
                return redirect(request.GET['next'])
            elif "random" in context["currentsearch"]:
                """
                If coming from random product page,
                then redirect to the same product as standard substitute page.
                """
                return HttpResponseRedirect(
                    reverse_lazy(
                        'product_substitutes',
                        kwargs={'pk': context["currentsearch"].replace("random_", "")}
                        ),
                    )
            return HttpResponseRedirect(reverse_lazy('search_product'))
    return render(request, 'openuser/connexion.html', context)


@login_required
def user_account(request):
    context = {}
    context["favorites_number"] = len(request.user.profile.products.all())
    return render(request, 'openuser/account.html', context)


@login_required
def log_out(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('search_product'))


@login_required
def user_favorites(request):
    context = {}
    products_added = 0
    if request.method == "POST":
        try:
            for favorite in json.loads(request.FILES["json_file"].read())["favorites"]:
                product_to_add = Product.objects.get(pk=favorite["id"])
                if product_to_add not in request.user.profile.products.all():
                    request.user.profile.products.add(product_to_add)
                    product_to_add.favorized += 1
                    product_to_add.save()
                    products_added += 1
            context["log_message"] = str(products_added) + " produit(s) ajouté(s)"
        except UnicodeDecodeError:
            context["log_message"] = "Problème avec le fichier."
        except ObjectDoesNotExist:
            context["log_message"] = "Erreur dans le fichier."
    favorites = request.user.profile.products.all()
    paginator = Paginator(favorites, 6)
    page = request.GET.get('page')
    try:
        context["favorites"] = paginator.page(page)
    except PageNotAnInteger:
        context["favorites"] = paginator.page(1)
    except EmptyPage:
        context["favorites"] = paginator.page(paginator.num_pages)
    return render(request, 'openuser/favorites_p.html', context)


@login_required
def add_to_favorites(request, pk):
    context = {}
    product_to_add = Product.objects.all().filter(pk=pk).first()
    context['product'] = product_to_add
    if product_to_add:
        context['response'] = "Y a un produit."
        request.user.profile.products.add(product_to_add)
        product_to_add.favorized += 1
        product_to_add.save()
    else:
        context['response'] = "Y a PAS d'produit !"
    return render(request, 'openuser/favorites.html', context)


@login_required
def remove_from_favorites(request, pk):
    context = {}
    product_to_remove = request.user.profile.products.filter(pk=pk).first()
    request.user.profile.products.remove(product_to_remove)
    if product_to_remove.favorized > 0:
        product_to_remove.favorized -= 1
        product_to_remove.save()
    context['to_delete'] = product_to_remove
    return render(request, 'openuser/favorites.html', context)


@login_required
def export_favorites(request):
    favorites = {"favorites": []}
    for favorite in request.user.profile.products.all():
        favorites["favorites"].append(
            {
                "id": favorite.pk,
                "product_name": favorite.product_name,
                "barcode": favorite.barcode,
            }
        )
    response = HttpResponse(json.dumps(favorites), content_type= "application/json")
    response['Content-Disposition'] = "attachment; filename={}-favs.json".format(request.user)
    return response