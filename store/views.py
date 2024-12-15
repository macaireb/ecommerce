import django.core.exceptions
from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django.db.models import Q
import json
from cart.cart import Cart


def search(request):
    # Determine if they filled out the form
    if request.method == "POST":
        searched = request.POST['searched']
        # Lets query the product model
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        if not searched:
            messages.error(request, "Sorry that product does not exist please try again.")
            return render(request, "search.html", {})
        else:
            print(searched)
            return render(request, "search.html", {'searched': searched})
    else:
        print("Method is get")
        return render(request, "search.html", {})


def update_info(request):
    if request.user.is_authenticated:
        try:
            current_user = Profile.objects.get(user__id=request.user.id)
            # get original form
            form = UserInfoForm(request.POST or None, instance=current_user)
        except django.core.exceptions.ObjectDoesNotExist:
            current_user = Profile(user=request.user)
            form = UserInfoForm(request.POST, instance=current_user)

        try:
            shipping_user = ShippingAddress.objects.filter(user__id=request.user.id).first()
            # get user shipping form
            shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        except django.core.exceptions.ObjectDoesNotExist:
            ShippingAddress(user=request.user)
            shipping_form = ShippingForm(request.POST, instance=shipping_user)

        if form.is_valid():
            form.save()
        if shipping_form.is_valid():
            shipping_form.save()

            messages.success(request, "Your info has been updated!!")
            return redirect('home')
        return render(request, "update_info.html", {'form': form, 'shipping_form': shipping_form})
    else:
        messages.success(request, "You must be logged in to access that page")
        return redirect('home')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request,"Your password has been updated!!")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')

        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})

    else:
            messages.success(request, "You must be logged in to view that page")
            return redirect('home')

    return render(request, 'update_password.html', {})


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "User has been updated!!")
            return redirect('home')
        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.success(request, "You must be logged in to access that page")
        return redirect('home')


def category_summary(request):
    categories = Category.objects.all()
    return render(request, "category_summary.html", {'categories': categories})


def category(request, foo):
    #replace hyphens with spaces
    foo = foo.replace('-', ' ')
    # Grab the category from the url
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except:
        messages.success(request, ("There was an error, that category doesnt exist "))
        return redirect('home')

def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, "product.html", {'product': product})

def home(request):
    products = Product.objects.all()
    return render(request, "home.html", {'products': products})


def about(request):
    return render(request, "about.html", {})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # lets do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            # get saved cart from database
            saved_cart = current_user.old_cart
            # convert database string to python dictionary
            if saved_cart:
                # convert to dictionary using Json
                converted_cart = json.loads(saved_cart)

                #add loaded cart dictionary to session
                cart = Cart(request)

                #loop through the cart and add items to database
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, ("You have been logged in"))
            return redirect('home')
        else:
            messages.success(request, ("There was an error please try again"))
            return redirect('login')
    else:
        return render(request, "login.html", {})


def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out... Thanks for stopping by"))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Username created - please fill out your user info below"))
            return redirect('update_info')
        else:
            messages.success(request, ("Whooopps there was a problem registering, please try again"))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})

