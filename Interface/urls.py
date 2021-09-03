from django.views.generic import RedirectView
from django.urls import path
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='home/')),
    path('home/', views.home, name='home'),
    path('history/', views.history, name='history'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('profile/password/', views.password, name='password')
]
