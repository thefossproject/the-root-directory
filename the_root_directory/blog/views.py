from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, View

from .forms import FileForm, OwnerForm, UserForm
from .models import File, Owner
from .utils.markdown import create_markdown_content


def home(request):
    recent_files = File.objects.order_by("-created_at")[:2]
    context = {"recent_files": recent_files}
    return render(request, "blog/home.html", context)


class FilesView(ListView):
    model = File
    paginate_by = 5
    context_object_name = "file_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "CHECK SOME ROOT FILES"
        context["description"] = "Learn something new today!"
        return context


class OwnerFilesView(View):
    template_name = "blog/file_list.html"

    def get(self, request):
        if request.user.is_authenticated:
            context = {"file_list": File.objects.filter(owner__user=request.user.id)}
            context["title"] = "YOUR ROOT FILES"
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
                owner = Owner.objects.filter(user = request.user).first()
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


def render_markdown(request):
    if request.user.is_authenticated:
        markdown_content = create_markdown_content(request.content)  # to check
        return JsonResponse({"content": markdown_content})
    else:
        return redirect("login")


class FileDetailView(DetailView):
    model = File
    context_object_name = "file"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        markdown_content = create_markdown_content(self.object.content)
        context["markdown_content"] = markdown_content
        return context


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
