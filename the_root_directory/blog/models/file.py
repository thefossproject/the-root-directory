from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .owner import Owner


class File(models.Model):
    title = models.CharField(max_length=70)
    content = models.TextField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=70, default="", null=False)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name="files")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("file_detail", kwargs={"pk": self.pk, "slug": self.slug})

    @property
    def size_in_kilobytes(self):
        return len(self.content.encode("utf-8")) / 1000
