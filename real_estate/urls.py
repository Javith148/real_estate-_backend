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
    path('export-properties/', views.export_properties, name='export_properties'),
    path('agents/', views.Agentpage, name='agents'),
    path('add-agent/', views.add_agent, name='add_agent'),
    path('edit-agent/<int:agent_id>/', views.edit_agent, name='edit_agent'),
    path('delete-agent/<int:agent_id>/', views.delete_agent, name='delete_agent'),
    path('toggle-agent-status/<int:agent_id>/', views.toggle_agent_status, name='toggle_agent_status'),
    path('export-agents/', views.export_agents_excel, name='export_agents'),
]