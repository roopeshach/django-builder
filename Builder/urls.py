
from django.urls import include, re_path, path
from django.contrib import admin
from django.views.generic import RedirectView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve

schema_view = get_schema_view(
    openapi.Info(
        title='Builder API Docs',
        default_version='v2',
    )
)

urlpatterns = [

    re_path(r'^dj-rest-auth/', include('dj_rest_auth.urls')),
    re_path(r'^dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    re_path(r'^account/', include('allauth.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^accounts/profile/$', RedirectView.as_view(url='/', permanent=True), name='profile-redirect'),
    re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='api_docs')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Include schema-generated app URLs
urlpatterns += [
    re_path(r'^Website/', include('Website.urls')),
re_path(r'^Restaurant/', include('Restaurant.urls')),
re_path(r'^Inventory/', include('Inventory.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

admin.site.site_header = "Builder - Platform Admin"
admin.site.site_title = "Builder - Platform Admin Portal"
admin.site.index_title = "Welcome to Builder - Platform Portal"
        