from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"), 
    path("errors", views.system_errors, name="errors"),
    path("register", views.register, name="register"),
    path("login", auth_views.LoginView.as_view(), name="login"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),

    path("api/api_get_nursery_temp", views.api_get_nursery_temp, name="api-nursery-temp"),
    path("api/api_get_greenhouse_temp", views.api_get_greenhouse_temp, name="api-greenhouse-temp"),
    path("api/api_get_nursery_humidity", views.api_get_nursery_humidity, name="api-nursery-humidity"),
    path("api/api_get_water_temp", views.api_get_water_temp, name="api-water-temp"),
    path("api/api_get_equipment_status", views.api_get_equipment_status, name="api-equipment-status"),
    path("api/api_get_system_status", views.api_get_system_status, name="api-system-status")
]