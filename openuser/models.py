from django.db import models
from django.contrib.auth.models import User
from openfood.models import Product

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='profiles')

    def __str__(self):
        return "{}-profile (id={})".format(self.user.username, self.user.id)

