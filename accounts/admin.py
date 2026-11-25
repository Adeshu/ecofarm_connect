# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'phone', 'first_name', 'last_name', 'total_points', 'level', 'is_verified', 'date_joined')
    list_filter = ('level', 'is_verified', 'state', 'district', 'date_joined')
    search_fields = ('email', 'phone', 'first_name', 'last_name', 'village')
    ordering = ('-total_points',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Location', {'fields': ('state', 'district', 'village')}),
        ('Gamification', {'fields': ('total_points', 'level', 'is_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'first_name', 'last_name', 'password1', 'password2', 'state', 'district', 'village'),
        }),
    )

    readonly_fields = ('date_joined',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'farming_experience_years', 'preferred_farming_type', 'created_at')
    list_filter = ('farming_experience_years', 'preferred_farming_type', 'created_at')
    search_fields = ('user__email', 'user__phone', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)
