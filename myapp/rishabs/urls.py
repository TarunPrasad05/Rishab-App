from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="index" ),
    path('login', views.login_view, name="login_view" ),
    path('register', views.register_view, name="register_view" ),
    path('logout', views.logout_view, name="logout_view" ),
    path('verify',views.verify, name="verify" ),
    path('order',views.order,name="order"),
    path('profile',views.profile_view,name="profile_view"),
    path('rorders/<int:pk>/', views.rorder_details, name="rorder_details"),
    path('feedback/', views.feedback, name="feedback")

]