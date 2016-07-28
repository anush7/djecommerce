from django.conf.urls import include, url
from carts import views


urlpatterns = [

	url(r'^cart$', views.CartView.as_view(), name='staff-product-liswwt'),

]