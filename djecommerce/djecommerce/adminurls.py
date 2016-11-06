from django.conf.urls import include, url
from users import adminviews as views

urlpatterns = [

	url(r'^staff-invite$', views.StaffInviteView.as_view(), name='staff_invite'),
    url(r'^staff-management$', views.StaffManagementView.as_view(), name='staff_management'),
    url(r'^staff-role$', views.StaffRoleView.as_view(), name='staff_role'),
    url(r'^staff-role/(?P<pk>\d+)$', views.StaffRoleView.as_view(), name='staff_role_action'),

    url(r'^tax$', views.TaxListView.as_view(), name='tax_list'),
    url(r'^tax/add$', views.TaxFormView.as_view(), name='tax_add'),
	url(r'^tax/(?P<pk>\d+)$', views.TaxFormView.as_view(), name='tax_update'),
	url(r'^tax/delete/(?P<pk>\d+)$', views.TaxDeleteView.as_view(), name='tax_delete'),

	url(r'^shipping$', views.ShippingFormView.as_view(), name='shipping_settings'),

	url(r'^currency$', views.CurrencyFormView.as_view(), name='currency_settings'),


	
]