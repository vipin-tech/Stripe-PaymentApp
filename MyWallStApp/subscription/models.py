from django.db import models
from django.utils import timezone


class PaymentMethod(models.Model):
    class Meta:
        db_table = 'payment_method'

    id = models.CharField(max_length=200, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    card_number = models.IntegerField()
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    cvc = models.IntegerField()


class Customer(models.Model):
    class Meta:
        db_table = 'customer'

    id = models.CharField(max_length=200, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_id = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)


class Subscription(models.Model):
    class Meta:
        db_table = 'subscription'

    id = models.CharField(max_length=200, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscription_status = models.CharField(max_length=200)
    price_id = models.CharField(max_length=200)
    purchase_date = models.DateTimeField(auto_now_add=True)

    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)


