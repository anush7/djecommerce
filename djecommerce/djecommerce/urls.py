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

    url(r'^signup$', views.user_signup, name='user_signup'),
    url(r'^login$', views.user_signin, name='user_signin'),
    url(r'^logout$', logout, {'template_name': 'users/signin.html','next_page':'/'},name='signout'),
    url(r'^forgot-password$', views.forgot_password, name='forgot_password'),
    url(r'^reset-password$', views.reset_password, name='rest_password'),
    
    url(r'^', include('products.urls')),

    url(r'^account/', include('users.urls')),
    url(r'^staff/', include('djecommerce.staffurls')),
    url(r'^admin/', include('djecommerce.adminurls')),

    url(r'^cart$', CartView.as_view(), name='add-to-cart'),
    url(r'^cart/count$', CartCountView.as_view(), name='cart_count'),
    url(r'^checkout/address$', AddressSelectFormView.as_view(), name='order_address'),
    url(r'^checkout$', CheckoutView.as_view(), name='checkout'),
    url(r'^checkout/final/$', CheckoutFinalView.as_view(), name='checkout_final'),
    
    url(r'^access-denied$', views.access_denied, name='user-access-denied'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)