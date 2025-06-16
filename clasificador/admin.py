from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_active', 'date_joined')  # Campos que se mostrarán
    search_fields = ('username', 'email', 'phone')  # Campos por los que se puede buscar
    list_filter = ('is_active', 'is_staff', 'is_superuser')  # Filtros disponibles
    ordering = ('date_joined',)  # Orden por defecto

admin.site.register(CustomUser, CustomUserAdmin)
