from django.conf.urls import include, url
from users import adminviews as views

urlpatterns = [

	url(r'^staff-invite$', views.StaffInviteView.as_view(), name='staff_invite'),
    url(r'^staff-management$', views.StaffManagementView.as_view(), name='staff_management'),
    url(r'^staff-role$', views.StaffRoleView.as_view(), name='staff_role'),
    url(r'^staff-role/(?P<pk>\d+)$', views.StaffRoleView.as_view(), name='staff_role_action'),
	
]