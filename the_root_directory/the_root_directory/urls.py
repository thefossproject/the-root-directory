from django.contrib import admin
from django.urls import include, path

from .settings import ENABLE_ADMIN

urlpatterns = [
    path("", include("blog.urls")),
]

if ENABLE_ADMIN:
    urlpatterns.append(path("admin/", admin.site.urls))
