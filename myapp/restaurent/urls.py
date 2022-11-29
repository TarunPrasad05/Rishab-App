from . import views
from django.urls import path

urlpatterns = [
    path('profile', views.profile_view_res, name="profile_view_res" ),
    path('dashboard', views.dashboard_view, name="dashboard_view" ),
    path('logout', views.logout_view, name="logout_view" ),
    path('orders/<int:pk>/', views.order_details, name="order_details")

]