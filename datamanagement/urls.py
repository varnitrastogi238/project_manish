from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('settings/', views.settings, name='settings'),
    path('stop_symbol/', views.stop_symbol, name='stop_symbol'),
    path('login_page/', views.login_page, name='/'),
    path('position/', views.position, name='position'),
    path('start_strategy/', views.start_strategy, name='start_strategy'),
    path('order/', views.closed_positions, name='start_strategy'),
    path('handleLogin/', views.handleLogin, name='/handleLogin'),
    path('handleLogout/', views.handleLogout, name='/handleLogout'),
]