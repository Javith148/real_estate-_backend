from django.urls import path
from . import views

urlpatterns = [
    path('api/property_details/', views.property_details_api, name='property_details_api'),
]