from django.conf import settings
from django.conf.urls import include, url
from users import views, stats
from orders.views import OrderList, OrderDetail

urlpatterns = [

    url(r'^dashboard$', views.dashboard, name='staff-dashboard'),

    #stats
    url(r'^stats/revenue-stats$', stats.revenue_stats, name='revenue-stats'),
    url(r'^stats/product-stats$', stats.product_stats, name='product-stats2'),
    
    url(r'^profile/(?P<pk>\d+)$', views.UserProfileUpdateView.as_view(), name='user_profile'),
    url(r'^orders$', OrderList.as_view(), name='orders'),
    url(r'^orders/(?P<pk>\d+)$', OrderDetail.as_view(), name='order_detail'),
    url(r'^change-password$', views.change_password, name='change-password'),

    url(r'^addresses$', views.UserAddressListView.as_view(), name='user_address_list'),
    url(r'^address/add$', views.UserAddressCreateView.as_view(), name='user-address-add'),
    url(r'^address/update/(?P<pk>\d+)$', views.UserAddressUpdateView.as_view(), name='user-address-update'),
    url(r'^address/delete/(?P<pk>\d+)$', views.delete_address, name='user-address-delete'),

    url(r'^check-username-email$', views.check_username_email, name='check-username-email'),
]