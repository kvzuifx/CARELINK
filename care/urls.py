from django.urls import path
from django.contrib import admin
from . import views
from .views import Index, dash, AddItem, EditItem
from .views import chat_view

urlpatterns = [
    path('', views.home12, name='home'),  # Added a name argument for consistency
    path('inven/', Index.as_view(), name='index'),
    path('dashboard/<int:user_id>/', views.dash, name='dash'),
    path('add-item/<int:user_id>/', AddItem, name='add-item'),
    path('inve/edit-item/<int:user_id>/<int:item_id>/', EditItem, name='edit-item'),    path("login/",views.loginPage, name="login"),
    path("register/",views.registerPage, name="register"),
    path("logout/", views.logOutUser, name="logout"),
    path('<int:user_id>/user/', views.userPage, name='user_page'), 
    path('location_suggestions/', views.location_suggestions, name='location_suggestions'),
    # path('index/', views.index1, name='index1'),
    path('distances/<int:user_id>/', views.distance_info, name='distance_info'),
    path('notifications/<int:user_id>/', views.notifications, name='notifications'),
    path('notifications/mark_as_read/<int:notif_id>/', views.mark_as_read, name='mark_as_read'),
     path('analytics/', views.Analytics, name='Analytics'),
    
    path('benefactor/<int:user_id>/requests/', views.requests_for_benefactor, name='benefactor_requests'),
 
     path('chat/', views.chat_view, name='chat_view'),

    path('upload_id_proof/<int:user_id>/', views.upload_id_proof, name='upload_id_proof'),
    path('view_id_proof/<int:user_id>/', views.view_id_proof, name='view_id_proof'),
]
