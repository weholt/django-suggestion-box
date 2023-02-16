from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("suggestion-box/", include("suggestion_box.urls")),
]
