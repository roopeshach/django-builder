
from django.urls import include, re_path, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve

urlpatterns = [
  
    re_path(r'^', include('app_builder.urls')),
    re_path(r'^admin/', admin.site.urls),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

admin.site.site_header = "Builder - Platform Admin"
admin.site.site_title = "Builder - Platform Admin Portal"
admin.site.index_title = "Welcome to Builder - Platform Portal"
        