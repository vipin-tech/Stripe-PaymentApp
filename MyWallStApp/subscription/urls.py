from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-subscription', views.subscription_view, name='subscription'),
    path('webhook', views.webhook_view, name='webhook'),
]