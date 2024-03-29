from django.contrib import admin
from django.urls import path
from authorization import views

urlpatterns = [
    path('reg', views.reg),
    path('auth', views.authorization)
]
