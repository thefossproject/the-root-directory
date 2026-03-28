from django.forms import ModelForm

from blog.models.owner import Owner


class OwnerForm(ModelForm):
    class Meta:
        model = Owner
        fields = ["biography"]
