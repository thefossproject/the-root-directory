from typing import Optional

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.generic import ListView, View

from .forms import FileForm, OwnerForm, UserForm
from .models import File, Owner
from .utils.markdown import create_markdown_content


def home(request):
    recent_files = File.objects.order_by("-created_at")[:3]
    context = {"recent_files": recent_files}
    return render(request, "blog/home.html", context)


def about(request):
    return render(request, "blog/about.html")


class FilesView(ListView):
    model = File
    paginate_by = 10
    context_object_name = "file_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["description"] = "Learn something new today!"
        return context


class OwnerFilesView(View):
    template_name = "blog/file_list.html"

    def get(self, request):
        if request.user.is_authenticated:
            context = {"file_list": File.objects.filter(owner__user=request.user.id)}
            context["description"] = "Look what you have created!"
            return render(request, self.template_name, context)
        else:
            return redirect("login")


class CreateFileView(View):
    template_name = "blog/create_file.html"

    def get_form(self, data):
        file_form = FileForm(data.POST)
        return {"file_form": file_form}

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, self.template_name, self.get_form(request))
        else:
            return redirect("login")

    def post(self, request):
        if request.user.is_authenticated:
            form = self.get_form(request)
            if form["file_form"].is_valid():
                file: File = form["file_form"].save(commit=False)
                owner = Owner.objects.filter(user=request.user).first()
                if owner is None:
                    messages.error(request, "The owner does not exist")
                    redirect("owner_files")
                file.owner = owner
                file.save()
                messages.success(request, "File created successfully!")
                return redirect("owner_files")
            else:
                return render(request, self.template_name, form)
        else:
            return redirect("login")

class UpdateFileView(View):
    template_name = "blog/update_file.html"

    def update_file(self, current_file: File, updated_file: File) -> File:
        changed_fields = []
        if current_file.title != updated_file.title:
            current_file.title = updated_file.title
            changed_fields.append("title")

            updated_slug = slugify(updated_file.title)
            if current_file.slug != updated_slug:
                current_file.slug = updated_slug
                changed_fields.append("slug")

        if current_file.content != updated_file.content:
            current_file.content = updated_file.content
            changed_fields.append("content")

        if changed_fields:
            current_file.save(update_fields=changed_fields)
        return current_file

    def get(self, request, pk):
        if request.user.is_authenticated:
            file_related = file_related_to_user(pk, request.user.id)
            if file_related:
                return render(
                    request, self.template_name, {"file_form": FileForm(instance=file_related)}
                )
            else:
                return redirect("owner_files")
        else:
            return redirect("login")

    def post(self, request, pk):
        if request.user.is_authenticated:
            form = FileForm(request.POST)
            if form.is_valid():
                current_file = file_related_to_user(pk, request.user.id)
                if current_file:
                    file_form: File = form.instance
                    updated_file = self.update_file(current_file, file_form)

                    messages.success(request, f"File '{updated_file.title}' updated!")
                    return redirect("owner_files")
                else:
                    return redirect("owner_files")
            else:
                return render(request, self.template_name, form)
        else:
            return redirect("login")


REQUEST_LIMIT = 20
TIME_WINDOW = 60


def render_markdown(request):
    if request.method == "POST" and request.user.is_authenticated:
        client = request.user.id
        key = f"rl:{client}"
        count = cache.get(key)
        if count is None:
            cache.set(key, 1, TIME_WINDOW)
        else:
            if count >= REQUEST_LIMIT:
                messages.warning(request, "Too much requests. Please wait before preview")
                return JsonResponse({"error": "rate limited"}, status=429)
            else:
                cache.set(key, count + 1, TIME_WINDOW)
        markdown_content = create_markdown_content(request.POST.get("content", ""))
        return JsonResponse({"content": markdown_content})
    else:
        return redirect("login")


def file_related_to_user(file_pk: int, user_id: int) -> Optional[File]:
    current_file = File.objects.filter(owner__user=user_id, pk=file_pk).first()
    return current_file


class FileDetailView(View):
    template_name = "blog/file_detail.html"

    def get(self, request, pk, slug):
        file = get_object_or_404(File, pk=pk, slug=slug)
        markdown_content = create_markdown_content(file.content)
        context = {"file": file, "markdown_content": markdown_content}
        if request.user.is_authenticated:
            file_related_to_auth_user = file_related_to_user(pk, request.user.id)
            if file_related_to_auth_user:
                context["update_file_url"] = reverse("update_file", kwargs={"pk": pk})
        return render(request, self.template_name, context)


class RegisterView(View):
    template_name = "blog/register.html"

    def get_forms(self, data):
        user_auth_form = UserCreationForm(data.POST)
        user_form = UserForm(data.POST or None)
        owner_form = OwnerForm(data.POST or None)
        return {"user_form": user_form, "owner_form": owner_form, "user_auth_form": user_auth_form}

    def get(self, request):
        return render(request, self.template_name, self.get_forms(request))

    def post(self, request):
        forms = self.get_forms(request)
        if all(form.is_valid() for form in forms.values()):
            with transaction.atomic():
                auth_user: User = forms["user_auth_form"].save(commit=False)
                user: User = forms["user_form"].save(commit=False)
                user.username = auth_user.username
                user.password = auth_user.password
                user.save()
                owner: Owner = forms["owner_form"].save(commit=False)
                owner.user = user
                owner.save()
                messages.success(request, "Owner created successfully!")
            return redirect("welcome")
        return render(request, self.template_name, forms)


def welcome(request):
    return render(request, "blog/welcome.html")
