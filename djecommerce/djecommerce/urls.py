from django.conf.urls import include, url
from django.contrib.auth.views import logout
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from users import views
from carts.views import CartView, CartCountView, CheckoutView, CheckoutFinalView
from orders.views import OrderList, OrderDetail, AddressSelectFormView, UserAddressCreateView

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^dd$', views.home, name="home"),
    
    url(r'^', include('products.urls')),

    url(r'^landing$', views.landing, name="landing"),
    url(r'^users/', include('users.urls')),
    url(r'^staff/', include('djecommerce.staffurls')),

    url(r'^cart/?$', CartView.as_view(), name='add-to-cart'),
    url(r'^cart/count$', CartCountView.as_view(), name='cart_count'),
    url(r'^checkout/$', CheckoutView.as_view(), name='checkout'),

    url(r'^checkout/address/$', AddressSelectFormView.as_view(), name='order_address'),
    url(r'^checkout/address/add/$', UserAddressCreateView.as_view(), name='user_address_create'),
    url(r'^checkout/final/$', CheckoutFinalView.as_view(), name='checkout_final'),

    url(r'^orders/$', OrderList.as_view(), name='orders'),
    url(r'^orders/(?P<pk>\d+)/$', OrderDetail.as_view(), name='order_detail'),

    url(r'^accounts/settings/?$', views.account_settings, name='account_settings'),
    url(r'^accounts/settings/change-password$', views.change_password, name='change-password'),

    url(r'^accounts/signup/$', views.user_signup, name='user_signup'),
    url(r'^accounts/login/$', views.user_signin, name='user_signin'),
    url(r'^signout/$', logout, {'template_name': 'account/signin.html','next_page':'/'},name='signout'),

    url(r'^accounts/forgot-password/$', views.forgot_password, name='forgot_password'),
    url(r'^accounts/reset-password/$', views.reset_password, name='rest_password'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)