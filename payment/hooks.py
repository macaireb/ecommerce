from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time
from .models import Order


@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    # Add a 5 second pause, waiting for paypal to send IPN data
    time.sleep(5)
    # Grab the info that paypal sends
    paypal_obj = sender
    # Grab the invoice
    my_invoice = str(paypal_obj.invoice)

    # match the paypal invoice to the order invoice
    # look up the order
    my_order = Order.objects.filter(invoice=my_invoice).first()

    # record order as paid
    my_order.paid = True

    # save order
    my_order.save()
    print(paypal_obj)
    print(f" Amount paid: {paypal_obj.mc_gross}")
