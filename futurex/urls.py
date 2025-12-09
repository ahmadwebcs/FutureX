from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from django.http import HttpResponse
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


def health(request):
    return HttpResponse('OK')

schema_view = get_schema_view(
   openapi.Info(
      title="FutureX API",
      default_version='v1',
      description="API documentation for FutureX platform",
      terms_of_service="",
      contact=openapi.Contact(email="contact@futurex.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health),
    path('api/investors/', include('apps.investors.urls')),
    path('api/investments/', include('apps.investments.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/admissions/', include('apps.admissions.urls')),
    path('api/auth/', include('rest_framework.urls')),
    # Accept both with and without trailing slash to avoid RuntimeError
    path('api/token-auth', obtain_auth_token),
    path('api/token-auth/', obtain_auth_token),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
