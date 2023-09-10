from django.urls import path
from myecomapp import views

urlpatterns = [
   path('',views.index, name="index"),

   path('contact',views.contact, name="contact"),

   path('about',views.about, name="about"),

   path('checkout/', views.checkout, name="Checkout"),

   path('profile/', views.profile, name="profile"),

   path('handlerequest/', views.handlerequest, name="HandleRequest")
]