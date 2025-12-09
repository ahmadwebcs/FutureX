from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from django.http import HttpResponse


def health(request):
    return HttpResponse('OK')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health),
    path('api/investors/', include('apps.investors.urls')),
    path('api/investments/', include('apps.investments.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/auth/', include('rest_framework.urls')),
    # Accept both with and without trailing slash to avoid RuntimeError
    path('api/token-auth', obtain_auth_token),
    path('api/token-auth/', obtain_auth_token),
]
