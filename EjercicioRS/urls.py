from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('', views.inicio),
    path('cargar/', views.cargar), 
    path('admin/',admin.site.urls),
    ]
