from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # These are base pages. i.e when a angularjs link is directly open in browser, a server request will be made and
    #  That request should serve the base angularjs app. along with auth check
    url(r'^$',views.ops_index, {"template_name": "opsPanel/public/index.html"},name='ops_dashboard'),
    url(r'^user-inquiry/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^crew-dashboard/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^ws-scheduler/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^workshops/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^recordings/(?P<param>[^/]+)/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^alerts/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^alerts/raise-alert/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^reports/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^reports/(?P<param>[^/]+)/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^reports/followups/(?P<param>[^/]+)/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^reports/feedback/(?P<param>[^/]+)/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^user-inquiry/edit-inquiry/(?P<param>[^/]+)/$$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^user-inquiry/create-inquiry/(?P<param>[^/]+)/$$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^bookings/$',views.ops_index, {"template_name": "opsPanel/public/index.html"},name='bookings'),
    url(r'^bookings/editBooking/(?P<param>[^/]+)/$',views.ops_index, {"template_name": "opsPanel/public/index.html"},name='edit_bookings'),
    url(r'^bookings/editBooking/(?P<param>[^/]+)/(?P<param2>[^/]+)/$',views.index_with_two_params, {"template_name": "opsPanel/public/index.html"}),
    url(r'^part-docs/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^part-docs/details/(?P<param>[^/]+)/(?P<param2>[^/]+)/$',views.index_with_two_params, {"template_name": "opsPanel/public/index.html"}),
    url(r'^users/edit-user/(?P<param>[^/]+)/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^users/edit-user-car/(?P<param>[^/]+)/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),

    url(r'^create-user/booking/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^create-user/inquiry/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^create-user/booking/add-user-car/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^create-user/booking/add-package/$',views.ops_index, {"template_name": "opsPanel/public/index.html"}),
    url(r'^users/$',views.ops_index, {"template_name": "opsPanel/public/index.html"},name='users'),
    url(r'^campaigns/scratch-finders/$',views.ops_index, {"template_name": "opsPanel/public/index.html"},name='scratchFinders'),
    url(r'^campaigns/all-leads/$',views.ops_index, {"template_name": "opsPanel/public/index.html"},name='allLeads'),
    url(r'^notify-users/$',views.ops_index, {"template_name": "opsPanel/public/index.html"},name='notify-users'),

    url(r'^login/$', auth_views.login, name='auth_login'),
    url(r'^logout/$', auth_views.logout, name='auth_logout'),
    url(r'^forgot-password/$', views.forgot_password, {"template_name":"registration/forgot_password.html"}, name='forgot_password'),
    url(r'^change-password/$', views.change_password, name='change_password'),
    # url(r'^logout/$', views.logout, name='auth_logout'),
    url(r'^verify_email/',views.verify_email,name='verify-email'),
]
