from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("avatar", "date_joined",)
    fieldsets = UserAdmin.fieldsets + (("Additional info", {"fields": ("avatar",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Additional info", {"fields": ("avatar", "date_joined")}),)
