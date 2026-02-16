from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),  # your app urls
    path("store-owner/", include("accounts.store_owner.urls")),
    path("delivery/", include("delivery.urls")),
    path('chaining/', include('smart_selects.urls')),
    path("bus/", include("accounts.bus_partner.urls")),

]

# Serve media files in development

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)