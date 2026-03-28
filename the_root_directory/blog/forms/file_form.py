from django import forms

from blog.models.file import File


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Title"}),
            "content": forms.Textarea(attrs={"placeholder": "Write the content here."})
        }
