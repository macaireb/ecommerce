from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.contrib import messages


def cart_summary(request):
    cart = Cart(request)
    print(f"Length is {str(cart.__len__())}")
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    return render(request, "cart_summary.html",
                  {'cart_products': cart_products, 'quantities': quantities, 'totals': totals})


def cart_add(request):
    # Get the cart
    cart = Cart(request)
    # test for POST
    if request.POST.get('action') == 'post':
        print("Action is type post lowercase")
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        # lookup product in DB
        product = get_object_or_404(Product, id=product_id)
        print(product.name)

        # Save to session
        cart.add(product=product, quantity=product_qty)
        print("Successfully returned from cart object add function... added new product to cart")

        # Get Cart Quantity
        cart_quantity = cart.__len__()
        print(f"Cart is of type: {type(cart)}")
        print(f"Cart quantity is of type: {type(cart_quantity)}")
        print(f"Cart quantity is: {cart_quantity}")

        # Return Response
        # response = JsonResponse(data={'Product Name: ': str(product.name)}, status=201)
        response = JsonResponse(data={'qty': cart_quantity}, status=201)
        messages.success(request, "Product added to cart...")
        return response


def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get stuff
        print(f"Post data is ID: {request.POST.get('product_id')}")
        product_id = int(request.POST.get('product_id'))
        # Call delete function in Cart
        cart.delete(product_id)
        response = JsonResponse(data={'product': product_id})
        messages.success(request, "Item deleted from shopping cart...")
        return response


def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get stuff
        print(f"Post data is ID: {request.POST.get('product_id')} Quantity is: {request.POST.get('product_qty')}")
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        cart.update(product=product_id, quantity=product_qty)
        response = JsonResponse(data={'qty': product_qty})
        messages.success(request, "Your cart has been updated...")
        return response
        #return redirect('cart_summary')