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

def registration(request):
    context = {}
    if "currentsearch" in request.session:
        context["currentsearch"] = request.session["currentsearch"]
    else:
        context["currentsearch"] = "logout"
    context["form"] = CreateUser(request.POST or None)
    if context["form"].is_valid():
        username = context["form"].cleaned_data['username']
        password = context["form"].cleaned_data['password']
        email = context["form"].cleaned_data['email']
        new_user = User.objects.create_user(username)
        new_user.set_password(password)
        new_user.email = email
        new_user.save()
        new_profile = Profile()
        new_profile.user = new_user
        new_profile.save()
        if authenticate(username=new_user.username, password=password):
            login(request, new_user)
            if "random" in context["currentsearch"]:
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
            else:
                return HttpResponseRedirect(reverse_lazy('search_product'))
    return render(request, 'openuser/registration.html', context)

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


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            # return HttpResponse('Please confirm your email address to complete the registration')
            return render(request, 'openuser/confirmation.html')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
        return render(request, 'openuser/activation_success.html', {})
    else:
        return render(request, 'openuser/activation_fail.html', {})
        # return HttpResponse('Activation link is invalid!')

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
    favorites = request.user.profile.products.all()
    paginator = Paginator(favorites, 6)
    page = request.GET.get('page')
    try:
        favorites_p = paginator.page(page)
    except PageNotAnInteger:
        favorites_p = paginator.page(1)
    except EmptyPage:
        favorites_p = paginator.page(paginator.num_pages)
    return render(request, 'openuser/favorites_p.html', {'favorites_p': favorites_p})

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
        # print(get_object_or_404(Product, pk=product_to_add.pk))
        # get_object_or_404(Product, pk=product_to_add.pk).update(favorized=9)
        
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