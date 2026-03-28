from django.contrib import admin

from .models import File, Owner


class FileAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Owner)
admin.site.register(File, FileAdmin)
