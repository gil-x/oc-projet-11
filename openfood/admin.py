from django.contrib import admin
from .models import Category, Product, Position


class PositionInline(admin.TabularInline):
    model = Position
    extra = 1

class CategoryAdmin(admin.ModelAdmin):
    inlines = (PositionInline,)

class ProductAdmin(admin.ModelAdmin):
    inlines = (PositionInline,)


admin.site.register(Position)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
