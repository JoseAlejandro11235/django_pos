from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Category, Product, ProductoCategoria


@login_required(login_url="/accounts/login/")
def CategoriesListView(request):
    context = {
        "active_icon": "products_categories",
        "categories": Category.objects.all()
    }
    return render(request, "products/categories.html", context=context)


@login_required(login_url="/accounts/login/")
def CategoriesAddView(request):
    context = {
        "active_icon": "products_categories",
        "category_status": Category.status.field.choices
    }

    if request.method == 'POST':
        # Save the POST arguements
        data = request.POST

        attributes = {
            "name": data['name'],
            "status": data['state'],
            "description": data['description']
        }

        # Check if a category with the same attributes exists
        if Category.objects.filter(**attributes).exists():
            messages.error(request, 'Category already exists!',
                           extra_tags="warning")
            return redirect('products:categories_add')

        try:
            # Create the category
            new_category = Category.objects.create(**attributes)

            # If it doesn't exists save it
            new_category.save()

            messages.success(request, 'Category: ' +
                             attributes["name"] + ' created succesfully!', extra_tags="success")
            return redirect('products:categories_list')
        except Exception as e:
            messages.success(
                request, 'There was an error during the creation!', extra_tags="danger")
            print(e)
            return redirect('products:categories_add')

    return render(request, "products/categories_add.html", context=context)


@login_required(login_url="/accounts/login/")
def CategoriesUpdateView(request, category_id):
    """
    Args:
        category_id : The category's ID that will be updated
    """

    # Get the category
    try:
        # Get the category to update
        category = Category.objects.get(id=category_id)
    except Exception as e:
        messages.success(
            request, 'There was an error trying to get the category!', extra_tags="danger")
        print(e)
        return redirect('products:categories_list')

    context = {
        "active_icon": "products_categories",
        "category_status": Category.status.field.choices,
        "category": category
    }

    if request.method == 'POST':
        try:
            # Save the POST arguements
            data = request.POST

            attributes = {
                "name": data['name'],
                "status": data['state'],
                "description": data['description']
            }

            # Check if a category with the same attributes exists
            if Category.objects.filter(**attributes).exists():
                messages.error(request, 'Category already exists!',
                               extra_tags="warning")
                return redirect('products:categories_add')

            # Get the category to update
            category = Category.objects.filter(
                id=category_id).update(**attributes)

            category = Category.objects.get(id=category_id)

            messages.success(request, '¡Category: ' + category.name +
                             ' updated successfully!', extra_tags="success")
            return redirect('products:categories_list')
        except Exception as e:
            messages.success(
                request, 'There was an error during the elimination!', extra_tags="danger")
            print(e)
            return redirect('products:categories_list')

    return render(request, "products/categories_update.html", context=context)


@login_required(login_url="/accounts/login/")
def CategoriesDeleteView(request, category_id):
    """
    Args:
        category_id : The category's ID that will be deleted
    """
    try:
        # Get the category to delete
        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(request, '¡Category: ' + category.name +
                         ' deleted!', extra_tags="success")
        return redirect('products:categories_list')
    except Exception as e:
        messages.success(
            request, 'There was an error during the elimination!', extra_tags="danger")
        print(e)
        return redirect('products:categories_list')


@login_required(login_url="/accounts/login/")
def ProductsListView(request):
    context = {
        "active_icon": "products",
        "products": Product.objects.all(),
        "productoscategorias": ProductoCategoria.objects.all()
    }
    return render(request, "products/products.html", context=context)


@login_required(login_url="/accounts/login/")
def ProductsAddView(request):
    context = {
        "active_icon": "products",
        "product_status": Product.status.field.choices,
        "categories": Category.objects.all().filter(status="ACTIVE")
    }

    if request.method == 'POST':
        # Save the POST arguements
        data = request.POST

        attributes = {
            "name": data['name'],
            "status": data['state'],
            "description": data['description'],
            "price": data['price']
        }
        

        # Check if a product with the same attributes exists
        if Product.objects.filter(**attributes).exists():
            messages.error(request, 'Product already exists!',
                           extra_tags="warning")
            return redirect('products:products_add')

        try:
            # Create the product
            new_product = Product.objects.create(**attributes)
            selected_categories = request.POST.getlist('category')
            for category_id in selected_categories:
                category = Category.objects.get(pk=category_id)
                attributes_productocategoria = {
                    "id_producto": new_product,
                    "id_categoria": category
                }
                new_productocategoria = ProductoCategoria.objects.create(**attributes_productocategoria)
                new_productocategoria.save()

            # ATRIBUTES TO ADD THE REGISTER TO THE TABLE PRODUCTCATEGORY
            

            new_productocategoria.save()

            messages.success(request, 'Product: ' +
                             attributes["name"] + ' created succesfully!', extra_tags="success")
            return redirect('products:products_list')
        except Exception as e:
            messages.success(
                request, 'There was an error during the creation!', extra_tags="danger")
            print(e)
            return redirect('products:products_add')

    return render(request, "products/products_add.html", context=context)


@login_required(login_url="/accounts/login/")
def ProductsUpdateView(request, product_id):
    try:
        # Get the product to update
        product = Product.objects.get(id=product_id)

        if request.method == 'POST':
            # Delete existing ProductoCategoria instances for this product
            ProductoCategoria.objects.filter(id_producto=product).delete()

            # Add new ProductoCategoria instances for selected categories
            selected_categories = request.POST.getlist('category')
            for category_id in selected_categories:
                category = Category.objects.get(pk=category_id)
                ProductoCategoria.objects.create(id_producto=product, id_categoria=category)

            # Update product attributes
            data = request.POST
            product.name = data['name']
            product.status = data['state']
            product.description = data['description']
            product.price = data['price']
            product.save()

            messages.success(request, f'Product: {product.name} updated successfully!', extra_tags="success")
            return redirect('products:products_list')

    except Product.DoesNotExist as e:
        messages.error(request, 'Product not found!', extra_tags="danger")
        print(e)
        return redirect('products:products_list')
    except Exception as e:
        messages.error(request, f'Error updating product: {e}', extra_tags="danger")
        print(e)
        return redirect('products:products_list')

    categories = Category.objects.all()
    product_categories = product.productocategoria_set.values_list('id_categoria', flat=True)

    context = {
        "active_icon": "products",
        "product_status": Product.STATUS_CHOICES,  # Use STATUS_CHOICES from the model
        "product": product,
        "categories": categories,
        "product_categories": product_categories,
    }

    return render(request, "products/products_update.html", context=context)






@login_required(login_url="/accounts/login/")
def ProductsDeleteView(request, product_id):
    """
    Args:
        product_id : The product's ID that will be deleted
    """
    try:
        # Get the product to delete
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(request, '¡Product: ' + product.name +
                         ' deleted!', extra_tags="success")
        return redirect('products:products_list')
    except Exception as e:
        messages.success(
            request, 'There was an error during the elimination!', extra_tags="danger")
        print(e)
        return redirect('products:products_list')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url="/accounts/login/")
def GetProductsAJAXView(request):
    if request.method == 'POST':
        if is_ajax(request=request):
            data = []

            products = Product.objects.filter(
                name__icontains=request.POST['term'])
            for product in products[0:10]:
                item = product.to_json()
                data.append(item)

            return JsonResponse(data, safe=False)
