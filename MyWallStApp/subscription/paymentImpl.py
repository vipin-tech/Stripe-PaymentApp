from django.conf import settings
import stripe
from .models import PaymentMethod, Customer, Subscription
# import the logging library
import logging

# Get an instance of a logging
LOG = logging.getLogger('django')


class PaymentImpl:
    def __init__(self, kwargs=None):
        self.kwargs = kwargs


class StripePayment(PaymentImpl):
    def __init__(self, **kwargs):
        PaymentImpl.__init__(self, **kwargs)
        self.price_plan = {'standard': settings.STANDARD_PRICE_PLAN}
        self.secret_key = settings.STRIPE_SECRET_KEY
        self.payment_id = None
        self.default_payment_source = None
        self.customer_id = None
        self.subscription_id = None

        # set the stripe api key
        stripe.api_key = self.secret_key

    def initiate_subscription(self):
        ret_val = {"status_code": 202, "status": "Success", "message": "Subscription Successful"}

        try:
            self.subscription_creation()
        except Exception as ex:
            ret_val = {"status_code": 500, "status": "Failed", "message": "Subscription Failed"}

        return ret_val

    def subscription_creation(self):
        try:
            '''
                Steps to create the subscription:
                
                1. Create the payment method.
                2. Create the Customer.
                3. Attach the payment id to the Customer created.
                4. Make this payment id as default payment source for this customer.
                5. Attach the Customer to the payment method.
                6. Create the subscription.
                7. Attach the Customer id to the subscription created.
                8. Using response sent by stripe webhook, update the subscription status in the subscription table 
                   accordingly.
            '''

            self.create_payment_method()
            self.create_customer()

            self.attach_payment_method()
            self.update_customer()

            self.create_subscription()
            self.update_subscription()
        except Exception as ex:
            raise ex

    def create_payment_method(self, payment_type='card'):
        kwargs = self.kwargs
        ret_val = stripe.PaymentMethod.create(
            type=payment_type,
            card={
                "number": kwargs.get('cardNumber'),
                "exp_month": kwargs.get('expiryMonth'),
                "exp_year": kwargs.get('expiryYear'),
                "cvc": kwargs.get('cvc'),
            },
        )

        self.payment_id = ret_val['id']

        # Save to the database
        payment_obj = PaymentMethod(id=self.payment_id, card_number=kwargs.get('cardNumber'),
                                    expiry_month=kwargs.get('expiryMonth'), expiry_year=kwargs.get('expiryYear'),
                                    cvc=kwargs.get('cvc'))
        payment_obj.save()

        LOG.info("Successfully created subscription method id= {}".format(self.payment_id))
        return ret_val

    def attach_payment_method(self):
        ret_val = stripe.PaymentMethod.attach(
            self.payment_id,
            customer=self.customer_id,
        )

        LOG.info("Successfully attached subscription method id={} to customer id={}".format(self.payment_id,
                                                                                            self.customer_id))
        return ret_val

    def create_customer(self):
        kwargs = self.kwargs
        ret_val = stripe.Customer.create(
            name=kwargs.get('name'),
            description="Description: " + kwargs.get('name'),
        )

        self.customer_id = ret_val['id']

        # Save the customer details to database
        payment_obj = PaymentMethod.objects.get(pk=self.payment_id)
        customer_obj = Customer(id=self.customer_id, payment_id=payment_obj, name=kwargs.get('name'),
                                email=kwargs.get('email'))
        customer_obj.save()

        LOG.info("Successfully created Customer id= {}".format(self.customer_id))
        return ret_val

    def update_customer(self):
        ret_val = stripe.Customer.modify(
            self.customer_id,
            invoice_settings={"default_payment_method": self.payment_id}
        )

        LOG.info("Successfully updated the Customer id= {} with payment id= {}".format(self.customer_id,
                                                                                            self.payment_id))
        return ret_val

    def create_subscription(self):
        kwargs = self.kwargs
        price_id = self.price_plan[kwargs.get('pricePlan', 'standard')]

        ret_val = stripe.Subscription.create(
            customer=self.customer_id,
            items=[
                {"price": price_id},
            ],
        )

        self.subscription_id = ret_val['id']

        # Save the subscription to the database
        customer_obj = Customer.objects.get(pk=self.customer_id)
        subscription_obj = Subscription(id=self.subscription_id,
                                        price_id=price_id,
                                        customer_id=customer_obj)
        subscription_obj.save()

        LOG.info("Successfully created the Subscription id= {}".format(self.subscription_id))
        return ret_val

    def update_subscription(self):
        ret_val = stripe.Subscription.modify(
            self.subscription_id,
            metadata={"customer": self.customer_id, }
        )

        LOG.info("Successfully updated the Subscription id={}".format(self.subscription_id))
        return ret_val


    def update_subscription_data_in_db(self, data):
        subscription_obj = Subscription.objects.get(pk=data.get('id'))
        subscription_obj.subscription_status = data.get('status')
        subscription_obj.save()

        LOG.info("Successfully updated the subscription table with subscription status= {}".format(data.get('status')))
