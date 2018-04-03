from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('views/', include('config.urls.views')),
    path('', include('config.urls.apis'))
]
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)
