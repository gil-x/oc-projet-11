from django.test import RequestFactory, TestCase, Client  
# from django.test import force_login
from django.contrib.auth.models import AnonymousUser, User
from .models import Profile
from openfood.models import Category, Product
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from .views import add_to_favorites, remove_from_favorites
from .forms import *
from django.core import mail
import json

class ProfileTests(TestCase):
    def setUp(self):
        """
        Appelée une seule fois avant tous les tests.
        Pour créer de la data, pas des variables.
        """
        username = 'jdoe'
        password = 'password'
        email = 'jdoe@me.org'
        new_user = User.objects.create_user(username='doe', email='jdoe@me.org')
        new_user.set_password('password')
        new_user.save()
        new_profile = Profile()
        new_profile.user = new_user
        new_profile.save()

        new_category = Category.objects.get_or_create(
                    category_name="spam",
                )

        new_product = Product()
        new_product.product_name = "egg"
        new_product.grade = "a"
        new_product.url = "http://eggs"
        new_product.barcode = "0123456789123"
        new_product.brand = "pythonic"
        new_product.store = "Spam Store"
        new_product.product_img_url = "http://eggs/picture.png"

        new_product.save()

        self.factory = RequestFactory()
        self.user = new_user
        self.product = new_product
   
    def test_user_creation(self):
        """
        Test new user creation.
        """
        username = 'Smith'
        password = 'password'
        email = 'smith@me.org'
        new_user = User.objects.create_user(username)
        new_user.set_password(password)
        new_user.email = email
        new_user.save()
        new_profile = Profile()
        new_profile.user = new_user
        new_profile.save()
        self.assertEqual(username, new_user.username)
        self.assertEqual(email, new_user.email)
        self.assertTrue(authenticate(username=new_user.username, password=password))

    def test_connexion_view(self):
        """
        Test the Connection page code response.
        """
        c = Client()
        response = c.get('/connexion/')
        self.assertEqual(response.status_code, 200)

    def test_add_to_favorites_user_anonymous(self):
        request = self.factory.get('/mon-espace/add-product/1/')
        request.user = AnonymousUser()
        response = add_to_favorites(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_add_to_favorites_user_authenticated(self):
        request = self.factory.get('/mon-espace/add-product/1/')
        request.user = self.user
        response = add_to_favorites(request, 1)
        self.assertEqual(response.status_code, 200)
    
    def test_remove_from_favorites_user_anonymous(self):
        request = self.factory.get('/mon-espace/add-product/1/')
        request.user = AnonymousUser()
        response = remove_from_favorites(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_remove_from_favorites_user_authenticated(self, pk=1):
        self.user.profile.products.add(self.product)
        request = self.factory.get('/mon-espace/remove-product/1/')
        request.user = self.user
        response = remove_from_favorites(request, 1)
        self.assertEqual(response.status_code, 200)

    def test_signup_form_valid(self):
        form = SignupForm(data={ 'username': 'steve', 'email': 'steve@me.org',
                'password1': 'greatestkey', 'password2': 'greatestkey' })
        # print("mail.outbox:", mail.outbox)
        #assertEqual mail size
        # il faut tester la vue !
        self.assertTrue(form.is_valid())

    def test_signup_form_not_valid(self):
        form = SignupForm(data={ 'username': 'steve', 'email': 'steve@me.org',
                'password1': 'greatestkey', 'password2': 'NOGREATKEY' })
        self.assertFalse(form.is_valid())

    def test_export_fav(self):
        c = Client()
        c.force_login(self.user, backend=None)
        request = self.factory.get('/mon-espace/add-product/1/')
        request.user = self.user
        response = add_to_favorites(request, 1)
        response = c.get('/mon-espace/export-favorites/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"favorites": [{"id": 1, "product_name": "egg", "barcode": "0123456789123"}]}')
