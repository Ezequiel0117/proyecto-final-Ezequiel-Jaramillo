from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('date_joined',)

admin.site.register(CustomUser, CustomUserAdmin)
