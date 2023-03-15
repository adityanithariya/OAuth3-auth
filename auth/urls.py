from django.contrib import admin
from django.urls import path, include

admin_urls = [
    path("admin/", admin.site.urls),
]

apps = [
    path("", include("app.urls")),
]

urlpatterns = [] + admin_urls + apps
