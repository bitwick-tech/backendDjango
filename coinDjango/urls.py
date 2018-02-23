from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('frequency/', views.frequency, name='frequency'),
    path('coins/', views.coins, name='coins'),
    path('coinsstaticdata/', views.get_all_coins_static_data),
    path('coinsstaticdata', views.get_all_coins_static_data),
    path('coinprice/', views.get_coin_price_api),
    path('coinprice', views.get_coin_price_api)
]
