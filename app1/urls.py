from django.urls import path
# from app1.views import data, index, productall, productfilter, login
from app1.views import *


urlpatterns = [
    path('data/', data),
    path('', index, name='index1'),
    path('product-all/', productall),
    path('product-filter/<int:id>/', productfilter),
    path('product-get/<int:id>/', productget, name='productdetails'),
    path('register/', register),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('contactus/', contactus),
    path('profile/', profile, name='profile1'),
    path('buynow/', buynow, name='buy'),
    path('ordertable/', ordertable, name='myorder'),
    path('ordersuccess/', ordersuccess, name='ordersuccess'),
    path('razarpayView/', razorpayView, name='razorpayView'),
    path('paymenthandler/', paymenthandler, name='paymenthandler')
]
