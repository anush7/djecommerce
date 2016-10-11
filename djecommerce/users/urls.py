from django.conf import settings
from django.conf.urls import include, url
from users import views

urlpatterns = [
	
	url(r'^signup/$', views.user_signup, name='user_signup'),
    url(r'^login/$', views.user_signin, name='user_signin'),

    url(r'^profile/(?P<pk>\d+)$', views.UserProfileUpdateView.as_view(), name='user_profile'),

    url(r'^staff-invite$', views.StaffInviteView.as_view(), name='staff_invite'),
    url(r'^staff-management$', views.StaffManagementView.as_view(), name='staff_management'),
    url(r'^staff-role$', views.StaffRoleView.as_view(), name='staff_role'),
    url(r'^staff-role/(?P<pk>\d+)$', views.StaffRoleView.as_view(), name='staff_role_action'),

	url(r'^settings/?$', views.account_settings, name='account_settings'),
    url(r'^settings/change-password$', views.change_password, name='change-password'),

    url(r'^forgot-password/$', views.forgot_password, name='forgot_password'),
    url(r'^reset-password/$', views.reset_password, name='rest_password'),

	url(r'^addresses$', views.UserAddressListView.as_view(), name='user_address_list'),
    url(r'^address/add/$', views.UserAddressCreateView.as_view(), name='user-address-add'),
    url(r'^address/update/(?P<pk>\d+)$', views.UserAddressUpdateView.as_view(), name='user-address-update'),
    url(r'^address/delete/(?P<pk>\d+)$', views.delete_address, name='user-address-delete'),

    url(r'^access-denied$', views.access_denied, name='user-access-denied'),
    url(r'^dashboard$', views.dashboard, name='staff-dashboard'),

    url(r'^check-username-email$', views.check_username_email, name='check-username-email'),
]