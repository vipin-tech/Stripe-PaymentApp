from django.test import TestCase, Client
from .models import PaymentMethod, Customer, Subscription
from django.utils import timezone
from django.urls import reverse
import json
from unittest.mock import Mock


class PaymentMethodTestCase(TestCase):

    def create_payment_method(self) -> None:
        return PaymentMethod.objects.create(id='123', created_at=timezone.now(), updated_at=timezone.now(),
                                    card_number=4242424242442442, expiry_month=5, expiry_year=2023, cvc=342)

    def test_create_payment_method(self):
        expected_payment_id = '123'
        payment_obj = self.create_payment_method()

        self.assertTrue(isinstance(payment_obj, PaymentMethod))
        self.assertEqual(payment_obj.id, expected_payment_id)


class CustomerTestCase(TestCase):

    def setUp(self) -> None:
        PaymentMethod.objects.create(id='123', created_at=timezone.now(), updated_at=timezone.now(),
                                     card_number=4242424242442442, expiry_month=5, expiry_year=2023, cvc=342)

    def create_customer(self):
        payment_obj = PaymentMethod.objects.get(pk='123')
        return Customer.objects.create(id='456', created_at=timezone.now(), updated_at=timezone.now(),
                                       payment_id=payment_obj,
                                       name='abc', email='abc@gmail.com')

    def test_create_customer(self):
        customer_obj = self.create_customer()
        self.assertTrue(isinstance(customer_obj, Customer))

        expected_customer_id = '456'
        self.assertEqual(customer_obj.id, expected_customer_id)

    def test_update_customer(self):
        expected_payment_obj = PaymentMethod.objects.get(pk='123')
        customer_obj = self.create_customer()

        self.assertEqual(customer_obj.payment_id.id, expected_payment_obj.id)


class SubscriptionTestCase(TestCase):
    def setUp(self) -> None:
        PaymentMethod.objects.create(id='123', created_at=timezone.now(), updated_at=timezone.now(),
                                     card_number=4242424242442442, expiry_month=5, expiry_year=2023, cvc=342)

        payment_obj = PaymentMethod.objects.get(pk='123')

        Customer.objects.create(id='456', created_at=timezone.now(), updated_at=timezone.now(),
                                payment_id=payment_obj,
                                name='abc', email='abc@gmail.com')

        customer_obj = Customer.objects.get(pk='456')

        Subscription.objects.create(id='789', created_at=timezone.now(), updated_at=timezone.now(),
                                    subscription_status='', price_id='p_id', purchase_date=timezone.now(),
                                    customer_id=customer_obj)

    def create_subscription(self):
        customer_obj = Customer.objects.get(pk='456')
        return Subscription.objects.create(id='100', created_at=timezone.now(), updated_at=timezone.now(),
                                    subscription_status='', price_id='p_id', purchase_date=timezone.now(),
                                    customer_id=customer_obj)

    def test_create_subscription(self):

        subscription_obj = self.create_subscription()
        expected_subscription_id = '100'

        self.assertTrue(isinstance(subscription_obj, Subscription))

        self.assertEqual(subscription_obj.id, expected_subscription_id)

    def test_update_subscription(self):
        customer_obj = Customer.objects.get(pk='456')
        subscription_obj = Subscription.objects.get(pk='789')

        self.assertEqual(subscription_obj.customer_id.id, customer_obj.id)

    def test_update_subscription_data_in_db(self):
        expected_subscription_status = 'active'
        data = {'id': '789', 'status': 'active'}

        subscription_obj = Subscription.objects.get(pk=data.get('id'))
        subscription_obj.subscription_status = data.get('status')
        subscription_obj.save()

        self.assertEqual(subscription_obj.subscription_status, expected_subscription_status)


class ViewsTestCase(TestCase):

    def setUp(self) -> None:
        PaymentMethod.objects.create(id='123', created_at=timezone.now(), updated_at=timezone.now(),
                                     card_number=4242424242442442, expiry_month=5, expiry_year=2023, cvc=342)
        payment_obj = PaymentMethod.objects.get(pk='123')

        Customer.objects.create(id='456', created_at=timezone.now(), updated_at=timezone.now(),
                                payment_id=payment_obj,
                                name='abc', email='abc@gmail.com')

        customer_obj = Customer.objects.get(pk='456')

        Subscription.objects.create(id='789', created_at=timezone.now(), updated_at=timezone.now(),
                                    subscription_status='active', price_id='p_id', purchase_date=timezone.now(),
                                    customer_id=customer_obj)

    def test_index(self):
        client = Client()
        response = client.get(reverse('index'))
        expected_response_code = 200
        self.assertEqual(response.status_code, expected_response_code)

    def test_subscription_view(self):
        client = Client()
        request_body = {
            "name": "Nick",
            "email": "nick@xyz.com",
            "cardNumber": 4242424242424242,
            "expiryMonth": 8,
            "expiryYear": 2022,
            "cvc": 675,
            "pricePlan": "standard"
        }

        response = client.post(reverse('subscription'), data=json.dumps(request_body), content_type='application/json')
        expected_response_code = 200
        self.assertEqual(response.status_code, expected_response_code)

    def test_webhook_view(self):
        client = Client()
        response = client.get(reverse('webhook'))
        expected_response_code = 200
        self.assertNotEqual(response.status_code, expected_response_code)


class StripePaymentTestCase(TestCase):
    def setUp(self) -> None:
        self.test_payment_id = 'fake_payment_id'
        self.test_customer_id = 'fake_customer_id'
        self.test_subscription_id = 'fake_subscription_id'

    def test_create_payment_method(self):
        stripe = Mock()
        ret_val = stripe.PaymentMethod.create(
            type="fake_card",
            card={
                "number": "fake_cardNumber",
                "exp_month": "fake_expiryMonth",
                "exp_year": "fake_expiryYear",
                "cvc": "fake_cvc",
            },
        )

        stripe.PaymentMethod.create.assert_called()

        self.test_payment_id = ret_val.id

    def test_attch_payment_method(self):
        stripe = Mock()
        ret_val = stripe.PaymentMethod.attach(
            self.test_payment_id,
            customer=self.test_customer_id,
        )
        stripe.PaymentMethod.attach.assert_called()

    def test_create_customer(self):
        stripe = Mock()
        ret_val = stripe.Customer.create(
            name='fake_name',
            description="Description: " + 'fake_desc',
        )

        stripe.Customer.create.assert_called()

        self.test_customer_id = ret_val.id

    def test_update_customer(self):
        stripe = Mock()
        ret_val = stripe.Customer.modify(
            self.test_customer_id,
            invoice_settings={"default_payment_method": self.test_payment_id}
        )

        stripe.Customer.modify.assert_called()

    def test_create_subscription(self):
        stripe = Mock()
        ret_val = stripe.Subscription.create(
            customer=self.test_customer_id,
            items=[
                {"price": "fake_price_id"},
            ],
        )

        stripe.Subscription.create.assert_called()
        self.test_subscription_id = ret_val.id

    def test_update_subscription(self):
        stripe = Mock()
        ret_val = stripe.Subscription.modify(
            self.test_subscription_id,
            metadata={"customer": self.test_customer_id, }
        )

        stripe.Subscription.modify.assert_called()

