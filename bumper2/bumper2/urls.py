from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.authtoken import views as token_views
from django.views.generic.base import TemplateView
from core import views
from api import urls
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'bumper2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, {"template_name": "public/index.html"}, name='index'),
    url(r'^core/', include('core.urls')),
    # for website urls refresh
    url(r'^select-package/$',views.index, {"template_name": "public/index.html"}),
    url(r'^select-car/$', views.index, {"template_name": "public/index.html"}),
    url(r'^choose-package/$', views.index, {"template_name": "public/index.html"}),
    url(r'^cart/$', views.index, {"template_name": "public/index.html"}),
    url(r'^sign-up/$', views.index, {"template_name": "public/index.html"}),
    url(r'^sign-up/login/$', views.index, {"template_name": "public/index.html"}),
    url(r'^sign-up/validate-otp/$', views.index, {"template_name": "public/index.html"}),
    url(r'^booking/cart/$', views.index, {"template_name": "public/index.html"}),
    url(r'^booking/schedule/account/$', views.index, {"template_name": "public/index.html"}),
    url(r'^booking/schedule/login/$', views.index, {"template_name": "public/index.html"}),
    url(r'^booking/schedule/validate-otp/$', views.index, {"template_name": "public/index.html"}),
    url(r'^packages/$', views.index, {"template_name": "public/index.html"}),
    url(r'^booking/schedule/$', views.index, {"template_name": "public/index.html"}),
    url(r'^booking/schedule/slot/$', views.index, {"template_name": "public/index.html"}),
    url(r'^booking/schedule/booking-complete/$', views.index, {"template_name": "public/index.html"}),
    url(r'^booking/schedule/address/$', views.index, {"template_name": "public/index.html"}),
    url(r'^schedule/$', views.index, {"template_name": "public/index.html"}),
    url(r'^schedule/pickup/$', views.index, {"template_name": "public/index.html"}),
    url(r'^schedule/drop/$', views.index, {"template_name": "public/index.html"}),
    url(r'^contact-us/$', views.index, {"template_name": "public/index.html"}),
    url(r'^car-wash/$', views.index, {"template_name": "public/index.html"}),
    url(r'^car-dent-scratch-remover/$', views.index, {"template_name": "public/index.html"}),
    url(r'^booking-status/$', views.index, {"template_name": "public/index.html"}),
    url(r'^payment/$', views.index, {"template_name": "public/index.html"}),
    url(r'^landing/$', views.index, {"template_name": "public/index.html"}),
    url(r'^car-dent-paint-body-repair-cost/$', views.index, {"template_name": "public/index.html"}),
    url(r'^about-us/$', views.index, {"template_name": "public/index.html"}),
    url(r'^contact/$', views.index, {"template_name": "public/index.html"}),
    url(r'^address/$', views.index, {"template_name": "public/index.html"}),
    url(r'^help/$', views.index, {"template_name": "public/index.html"}),
    url(r'^razorpay-success/$', views.index, {"template_name": "public/index.html"}),
    url(r'^workshop-network/$', views.index, {"template_name": "public/index.html"}),
    url(r'^how-it-works/$', views.index, {"template_name": "public/index.html"}),
    url(r'^customer-reviews/$', views.index, {"template_name": "public/index.html"}),
    url(r'^before-after/$', views.index, {"template_name": "public/index.html"}),
    url(r'^direct-payment/$', views.index, {"template_name": "public/index.html"}),
    url(r'^privacy-policy/$', views.index, {"template_name": "public/index.html"}),
    url(r'^feedback/$', views.index, {"template_name": "public/index.html"}),
    url(r'^inventory-list/$', views.index, {"template_name": "public/index.html"}),
    url(r'^electrical-list/$', views.index, {"template_name": "public/index.html"}),
    url(r'^whats-next/$', views.index, {"template_name": "public/index.html"}),
    url(r'^referral/$', views.index, {"template_name": "public/index.html"}),
    url(r'^car-photos/$', views.index, {"template_name": "public/index.html"}),
    url(r'^car-panels/$', views.index, {"template_name": "public/index.html"}),


    # For package desc
    url(r'^package/advance-interior-cleaning/$', TemplateView.as_view(template_name='package-desc/advance-interior-cleaning.html')),
    url(r'^package/exterior-car-beautification/$', TemplateView.as_view(template_name='package-desc/exterior-car-beautification.html')),
    url(r'^package/paint-protection/$', TemplateView.as_view(template_name='package-desc/paint-protection.html')),
    url(r'^package/ac-disinfection/$', TemplateView.as_view(template_name='package-desc/ac-disinfection.html')),
    url(r'^package/car-wash/$', TemplateView.as_view(template_name='package-desc/car-wash.html')),
    url(r'^package/full-body-paint/$', TemplateView.as_view(template_name='package-desc/full-body-paint.html')),
    url(r'^package/windshield-polish/$', TemplateView.as_view(template_name='package-desc/windsheild-polish.html')),
    url(r'^package/bumper-premium-protection/$', TemplateView.as_view(template_name='package-desc/bumper-premium-protection.html')),
    url(r'^package/full-body-color-change/$', TemplateView.as_view(template_name='package-desc/full-body-color-change.html')),
    url(r'^package/full-body-with-roof/$', TemplateView.as_view(template_name='package-desc/full-body-with-roof.html')),
    url(r'^package/what-is-dent-scratch/$', TemplateView.as_view(template_name='package-desc/dent-scratch-description.html')),
    url(r'^mailer-test/corporate-mailer/$', TemplateView.as_view(template_name='mailers/corporate_mailer.html')),


    url(r'^admin/', include(admin.site.urls)),

    # url(r'^accounts/login$', 'django.contrib.auth.views.login', name='auth_login'),
    url(r'^api-jwt-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^api/', include(urls)),
    url(r'^api-token-auth/', token_views.obtain_auth_token),
    #url('', include('social.apps.django_app.urls', namespace='social'))
    #url(r'^docs/', include('rest_framework_docs.urls')),
    #url(r'^docs/', views.docs),

    url(r'^sms/delivery-status/$',  views.sms_delivery_webhook),
    url(r'^payment/payu-success/$', views.payment_payu_success, {"template_name": "payment/payu-success.html"},
        name='payu-success'),
    url(r'^payment/payu-webhook/$', views.payment_payu_webhook, {"template_name": "payment/payu-success.html"},
        name='payu-webhook'),
    url(r'^payment/payu-fail/$', views.payment_payu_failure, {"template_name": "payment/payu-fail.html"},
        name='payu-fail'),

    url(r'^payment/citrus-pay/$', views.payment_citrus_pay, {"template_name": "payment/citrus-success.html"},
        name='citrus-success'),

    url(r'^payment/citrus-pay-web/$', views.payment_citrus_pay, {"template_name": "payment/citrus-success.html", "redirect_to_website": "1"},
        name='citrus-success'),

    url(r'^payment/citrus-pay-bill-gen/$', views.citrus_bill_generator, name='citrus-bill-gen'),

    url(r'^payment/citrus-pay-bill-gen-web/$', views.citrus_bill_generator_web, name='citrus-bill-gen-web'),
    url(r'^payment/citrus-pay-bill-gen-ios/$', views.citrus_bill_generator_ios),

    url(r'^payment/razor-pay/$', views.payment_razor_pay, {"template_name": "payment/citrus-success.html"},
        name='razor-success'),
]
