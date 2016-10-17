from django.conf.urls import include, url
from django.contrib.auth.views import logout
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from users import views
from carts.views import CartView, CartCountView, CheckoutView, CheckoutFinalView
from orders.views import OrderList, OrderDetail, AddressSelectFormView, UserAddressCreateView

urlpatterns = [
    url(r'^dd$', views.home, name="home"),
    url(r'^landing$', views.landing, name="landing"),
    
    url(r'^', include('products.urls')),

    url(r'^account/', include('users.urls')),
    url(r'^staff/', include('djecommerce.staffurls')),

    url(r'^cart$', CartView.as_view(), name='add-to-cart'),
    url(r'^cart/count$', CartCountView.as_view(), name='cart_count'),
    url(r'^checkout/address$', AddressSelectFormView.as_view(), name='order_address'),
    url(r'^checkout$', CheckoutView.as_view(), name='checkout'),
    url(r'^checkout/final/$', CheckoutFinalView.as_view(), name='checkout_final'),

    url(r'^account/orders$', OrderList.as_view(), name='orders'),
    url(r'^account/orders/(?P<pk>\d+)$', OrderDetail.as_view(), name='order_detail'),
    
    url(r'^signout$', logout, {'template_name': 'users/signin.html','next_page':'/'},name='signout'),


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)