from django.contrib import admin


from .models import Category, Product, ProductoCategoria

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductoCategoria)
