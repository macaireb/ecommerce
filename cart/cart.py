from store.models import Product, Profile


class Cart():
    def __init__(self, request):
        self.session = request.session

        # Get request
        self.request = request

        # Get the current session key if it exists
        cart = self.session.get('session_key')

        # If the user is new, no session key! Create one!
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}


        # Make sure cart is available on all pages of site
        self.cart = cart


    def db_add(self, product, quantity):
        product_id = str(product)
        product_quantity = quantity
        if product_id in self.cart:
            pass
        else:
            print("In cart object add function product id:" + product_id)
            print("Same place product price: " + str(product))
            #self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_quantity)
            print("Printing whats in the cart so far")
            print(self.cart[product_id])

        print("Trying to set session modification token to true")
        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # get current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # format string for Json, replacing ' ' with " "
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            print(f"Here's cart im about to save: {carty}")
            print(f"Here's the current user info before updating: {current_user}")
            # save carty to profile model
            current_user.update(old_cart=str(carty))
            print(f"Here's user info after update {current_user}")

    def add(self, product, quantity):
        product_id = str(product.id)
        product_quantity = quantity

        if product_id in self.cart:
            pass
        else:
            print("In cart object add function product id:" + product_id)
            print("Same place product price: " + str(product.price))
            #self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_quantity)
            print("Printing whats in the cart so far")
            print(self.cart[product_id])

        print("Trying to set session modification token to true")
        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # get current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # format string for Json, replacing ' ' with " "
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            print(f"Here's cart im about to save: {carty}")
            print(f"Here's the current user info before updating: {current_user}")
            # save carty to profile model
            current_user.update(old_cart=str(carty))
            print(f"Here's user info after update {current_user}")

    def cart_total(self):
        # Get product ids
        product_ids = self.cart.keys()
        # look up keys in product database model
        products = Product.objects.filter(id__in=product_ids)
        # Get Quantities
        quantities = self.cart
        # start counting at 0
        total = 0
        for key, value in quantities.items():
            #Convert key string into int so we can do math
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total = total + (product.sale_price * value)
                    else:
                        total = total + (product.price * value)
        return total



    def __len__(self):
        return len(self.cart)

    def get_prods(self):
        # Get product IDs from cart
        product_ids = self.cart.keys()

        # Use IDs to lookup products in database model
        products = Product.objects.filter(id__in=product_ids)

        # return those looked up products
        return products

    def get_quants(self):
        quantities = self.cart
        return quantities

    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)

        ourcart = self.cart
        #update dictionary/cart
        ourcart[product_id] = product_qty

        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # get current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # format string for Json, replacing ' ' with " "
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            print(f"Here's cart im about to save: {carty}")
            print(f"Here's the current user info before updating: {current_user}")
            # save carty to profile model
            current_user.update(old_cart=str(carty))
            print(f"Here's user info after update {current_user}")

        thing = self.cart
        return thing

    def delete(self, product):
        product_id = str(product)
        # Delete from dictionary/cart
        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True
        # Deal with logged in user
        if self.request.user.is_authenticated:
            # get current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # format string for Json, replacing ' ' with " "
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            print(f"Here's cart im about to update: {carty}")
            print(f"Here's the current user info before updating: {current_user}")
            # save carty to profile model
            current_user.update(old_cart=str(carty))
            print(f"Here's user info after update {current_user}")
