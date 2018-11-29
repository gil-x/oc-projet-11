from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404 # TODO Can I use it in Model Manager ?

class ProductManager(models.Manager):
    def get_substitutes(self, pk):
        context = {}
        # context['product'] = Product.objects.get(pk=pk)
        context['product'] = get_object_or_404(Product, pk=pk)
        # product = Product.objects.get(pk=pk)
        product = get_object_or_404(Product, pk=pk)
        categories = product.categories.all()
        positions = Position.objects.filter(product=context['product'])
        categories_and_rank = []

        for category in categories:
            categories_and_rank.append(
                (category.category_name, category.position_set.get(
                    category=category, product=product))
                )

        for category, rank in categories_and_rank:
            substitutes = Category.objects.filter(
                category_name=category).first().products.all().filter(
                Q(grade="a") | Q(grade="b")).order_by('?')[:6]
            if substitutes.count() != 0:
                context['substitutes'] = substitutes
                break

        if substitutes.count() == 0:
            context['substitutes'] = None # TODO The template should returns Error...

        return context

class Category(models.Model):
    category_name = models.CharField(max_length=255)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Catégories"


class Product(models.Model):
    product_name = models.CharField(max_length=255)
    grade = models.CharField(max_length=1)
    url = models.CharField(max_length=255)
    barcode = models.CharField(max_length=50)
    brand = models.CharField(max_length=255)
    store = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category, related_name='products', through='Position')
    product_img_url = models.CharField(max_length=255, null=True)
    favorized = models.IntegerField(default=0)
    objects = ProductManager()

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name_plural = "Produits"


class Position(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    rank = models.IntegerField()

    def __str__(self):
        return str(self.rank)