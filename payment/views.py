import django.core.exceptions
from django.shortcuts import render,redirect
from cart.cart import Cart
from .models import ShippingAddress
from .forms import ShippingForm, PaymentForm
from django.contrib import messages
from payment.models import Order, OrderItem
from store.models import Product, Profile
from django.contrib.auth.models import User
import datetime

# Create your views here.


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # get the order
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)
        if request.POST:
            status = request.POST['shipping_status'] == 'True'
            # check if true or false
            if status:
                # get order
                order = Order.objects.filter(id=pk)
                print(f"Order shipping status: {order[0].shipped}")
                # update status
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                # get order
                order = Order.objects.filter(id=pk)
                print(f"Order shipping status: {order[0].shipped}")
                # update status
                order.update(shipped=False, date_shipped=None)
            messages.success(request, "Shipped status updated")
            return redirect('home')

        return render(request, "payment/orders.html",{"order": order, "items": items})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status'] == 'True'
            num = request.POST['num']
            # get the order
            order = Order.objects.filter(id=num)
            # update status
            now = datetime.datetime.now()
            order.update(shipped=True, date_shipped=now)
            messages.success(request, "Shipped status updated")
            return redirect('shipped_dash')
        return render(request, "payment/not_shipped_dash.html",{"orders": orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status'] == 'True'
            num = request.POST['num']
            # get the order
            order = Order.objects.filter(id=num)
            # update status
            now = datetime.datetime.now()
            order.update(shipped=False, date_shipped=None)
            messages.success(request, "Shipped status updated")
            return redirect('unshipped_dash')
        return render(request, "payment/shipped_dash.html",{"orders": orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def process_order(request):
    if request.POST:
        cart = Cart(request)
        print(f"Length is {str(cart.__len__())}")
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        # Get billing info from last page
        payment_form = PaymentForm(request.POST or None)
        # get shipping session data
        my_shipping = request.session.get('my_shipping')
        print(my_shipping)
        # Create shipping address from order info
        shipping_address= (f" {my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}"
                           f"\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}"
                           f"\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}")
        print(shipping_address)

        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        amount_paid = totals

        if request.user.is_authenticated:
            # logged in
            user = request.user
            # Create Order
            create_order = Order(user=user,full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # get order ID
            order_id = create_order.pk
            # get product Info
            for product in cart_products:
                print("Looping through new product")
                # get product id
                product_id = product.id
                # get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                # get quantity
                for key, value in quantities.items():
                    print(f"Key is: {key}, Value is: {value}, product id is: {product.id}")
                    if int(key) == int(product.id):
                        # create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user,
                                                      quantity=value, price=price)
                        create_order_item.save()
                        print("Order item saved")

            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # delete session key
                    del request.session[key]

            # delete cart from database (old cart field in user)
            current_user = Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart="")

            messages.success(request, 'Order placed')
            return redirect('home')

        else:
            # not logged in
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            # get order ID
            order_id = create_order.pk
            # get product Info
            for product in cart_products:
                print("Looping through new product")
                # get product id
                product_id = product.id
                # get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                # get quantity
                for key, value in quantities.items():
                    print(f"Key is: {key}, Value is: {value}, product id is: {product.id}")
                    if int(key) == int(product.id):
                        # create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id,
                                                      quantity=value, price=price)
                        create_order_item.save()
                        print("Order item saved")
            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # delete session key
                    del request.session[key]

            messages.success(request, 'Order placed')
            return redirect('home')

    else:
        messages.success(request, 'Access Denied')
        return redirect('home')


def billing_info(request):
    if request.POST:
        cart = Cart(request)
        print(f"Length is {str(cart.__len__())}")
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()


        # Get shipping info form
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        #Check to see if user is logged in
        if request.user.is_authenticated:
            # Get billing form
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html",
               {'cart_products': cart_products, 'quantities': quantities, 'totals': totals,
                'shipping_info': request.POST, 'billing_form': billing_form})
        else:
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html",
                          {'cart_products': cart_products, 'quantities': quantities, 'totals': totals,
                           'shipping_info': request.POST, 'billing_form': billing_form})

    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def checkout(request):
    cart = Cart(request)
    print(f"Length is {str(cart.__len__())}")
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    if request.user.is_authenticated:
        # Checkout as logged in user
        try:
            shipping_user = ShippingAddress.objects.filter(user__id=request.user.id).first()
            shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        except django.core.exceptions.ObjectDoesNotExist or django.core.exceptions.Un:
            ShippingAddress(user=request.user)
            shipping_form = ShippingForm(request.POST, instance=shipping_user)
        return render(request, "payment/checkout.html",
                      {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})
    else:
        # Checkout as Guest
        shipping_form = ShippingForm(request.POST)
        return render(request, "payment/checkout.html",
                      {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})


def payment_success(request):

    return render(request, "payment/payment_success.html", {})

