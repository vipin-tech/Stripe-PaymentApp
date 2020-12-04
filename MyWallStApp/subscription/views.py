from django.shortcuts import render, redirect
from django.urls import reverse
from . import paymentImpl as impl
import json
from django.http.response import JsonResponse
from django.http import HttpResponse
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
# import the logging library
import logging

# Get an instance of a logging
LOG = logging.getLogger('django')


def index(request):
    return render(request, 'subscription/index.html')


def subscription_view(request):
    LOG.info("Initiate the product subscription request")

    stripe_impl = impl.StripePayment(kwargs=request.POST)

    # Initiate the subscription process
    response = stripe_impl.initiate_subscription()

    if response.get('status') == "Success":
        return render(request, "subscription/success.html")
    else:
        return render(request, "subscription/error.html")


@csrf_exempt
def webhook_view(request):
    LOG.info("stripe webhook invoked")
    payload = request.body
    event = None
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        event = stripe.Event.construct_from(
          json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    if event.type in ['customer.subscription.created', 'customer.subscription.updated']:
        # Update the subscription status
        stripe_impl = impl.StripePayment(kwargs=dict())
        stripe_impl.update_subscription_data_in_db(event.data.object)

    return HttpResponse(status=200)
