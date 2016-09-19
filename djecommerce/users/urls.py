from django.conf import settings
from django.conf.urls import include, url
from users import views

urlpatterns = [
	
	url(r'^signup/$', views.user_signup, name='user_signup'),
    url(r'^login/$', views.user_signin, name='user_signin'),

    url(r'^profile/(?P<pk>\d+)$', views.UserProfileUpdateView.as_view(), name='user_profile'),
    url(r'^user-management$', views.UserManagementView.as_view(), name='user_management'),
    url(r'^staff-permissions$', views.StaffPermissionView.as_view(), name='staff_permissions'),

	url(r'^settings/?$', views.account_settings, name='account_settings'),
    url(r'^settings/change-password$', views.change_password, name='change-password'),

    url(r'^forgot-password/$', views.forgot_password, name='forgot_password'),
    url(r'^reset-password/$', views.reset_password, name='rest_password'),

	url(r'^addresses$', views.UserAddressListView.as_view(), name='user_address_list'),
    url(r'^address/add/$', views.UserAddressCreateView.as_view(), name='user-address-add'),
    url(r'^address/update/(?P<pk>\d+)$', views.UserAddressUpdateView.as_view(), name='user-address-update'),
    url(r'^address/delete/(?P<pk>\d+)$', views.delete_address, name='user-address-delete'),

    url(r'^check-username-email$', views.check_username_email, name='check-username-email'),
]