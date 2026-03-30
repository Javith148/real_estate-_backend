from django.urls import path
from . import views

urlpatterns = [
    path('api/property_details/', views.property_details_api, name='property_details_api'),
    path('javith/', views.admin_login, name='login'),
    path('register/', views.create_admin, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('categories/', views.category, name='categories'),
    path('properties/', views.properties, name='properties'),
    path('add-property/', views.add_property, name='add_property'),
    path('edit-property/<int:property_id>/', views.edit_property, name='edit_property'),
    path('delete-property/<int:property_id>/', views.delete_property, name='delete_property'),
]