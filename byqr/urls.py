from django.contrib import admin
from django.urls import path, include
from meals.routers import router
from core.routers import router as core_router
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf.urls.i18n import i18n_patterns

# Web schema view
web_schema_view = SpectacularSwaggerView.as_view(url_name='schema')

# Mobile schema view
mobile_schema_view = SpectacularSwaggerView.as_view(url_name='mobile-schema')



urlpatterns = [
    path("admin/",admin.site.urls),
    # Include other apps' URLs
    path("", include("accounts.urls")),
    path("", include("base_user.urls")),
    path("", include("meals.urls")),
    path("", include("core.urls")),
    path("", include('hotels.urls')),
    path("", include("restaurants.urls")),
    path("", include('feedback.urls')),
    path("", include('iiko.urls')),
    path("", include("museums.urls")),


    # Mobile-related URLs
    path("mobile/", include("base_user.mobile_urls")),
    path("mobile/", include("feedback.mobile_urls")),
    path("mobile/", include("meals.mobile_urls")),
    path("mobile/", include("core.mobile_urls")),
    path("mobile/", include("loyalty.urls")),
    path("loyalty_latest/",include("loyalty_latest.api.urls")),

    # Schema views for DRF Spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api-doc/web', web_schema_view, name='schema-swagger-ui'),
    path('api-doc/mobile', mobile_schema_view, name='mobile-schema-swagger-ui'),

    # Router for core and meals
    path("", include(core_router.urls)),
    path('', include(router.urls)),
]

# Adding i18n support for internationalization
urlpatterns = [
    *i18n_patterns(*urlpatterns, prefix_default_language=False),
]

# Serve static and media files in development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
