from django.contrib import admin
from django.urls import path
from . import views
from .views import initiate_payment, verify_payment

urlpatterns = [
    path('', views.home, name='home'),
    path('pay/', initiate_payment),
    path('verify-payment/', verify_payment),
]
