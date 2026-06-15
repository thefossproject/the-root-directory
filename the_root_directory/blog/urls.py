from django.urls import include, path

from blog.views import CreateFileView, FileDetailView, FilesView, OwnerFilesView, RegisterView

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("files/", FilesView.as_view(), name="files"),
    path("files/<int:pk>/<slug:slug>/", FileDetailView.as_view(), name="file_detail"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("owner/register/", RegisterView.as_view(), name="register"),
    path("owner/welcome/", views.welcome, name="welcome"),
    path("owner/files", OwnerFilesView.as_view(), name="owner_files"),
    path("files/create", CreateFileView.as_view(), name="create_file"),
]
