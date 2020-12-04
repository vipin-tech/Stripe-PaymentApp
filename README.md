# Design and Implementation of Product Subscription using Django and Stripe APIs

---

The URL for the Product Subscription Application is:


[http://ec2-54-246-47-112.eu-west-1.compute.amazonaws.com/](http://ec2-54-246-47-112.eu-west-1.compute.amazonaws.com/)

---

The Stripe APIs used for Product subscription:

**Import Stripe Module**

> import stripe

---

**Create Payment Method**

> stripe.api_key = "obfuscated_offline_key"

> stripe.PaymentMethod.create(
>  type="card",
>  card={
>    "number": "4242424242424242",
>    "exp_month": 12,
>    "exp_year": 2021,
>    "cvc": "314",
>  },
> )

**Create Customer**

> stripe.api_key = "obfuscated_offline_key"

> stripe.Customer.create(
>   description="My First Test Customer (created for API docs)",
> )

**Attach PaymentMethod to Customer**

> stripe.api_key = "obfuscated_offline_key"

> stripe.PaymentMethod.attach(
>   "pm_1HuQgxCMJr6pYPABIl9zjtPs",
>   customer="cus_IUF29lk0d35PYu",
> )

**Modify the Customer to attach the payment_id as default payment source**

> stripe.api_key = "obfuscated_offline_key"

> stripe.Customer.modify(
>   "cus_IUF29lk0d35PYu",
>   metadata={"order_id": "6735"},
> )

**Create Subscription**

> stripe.api_key = "obfuscated_offline_key"

> stripe.Subscription.create(
>   customer="cus_IUF29lk0d35PYu",
>   items=[
>     {"price": "price_1HtEBFCMJr6pYPABaADQJK3V"},
>   ],
> )

Application logs can be found in subscription.log
