from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, DoctorProfile, PatientProfile, Appointment, HealthInsight


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = UserAdmin.list_filter + ('role',)


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'experience_years', 'phone', 'is_approved')
    list_filter = ('is_approved', 'specialization')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('patient__username', 'doctor__username')


@admin.register(HealthInsight)
class HealthInsightAdmin(admin.ModelAdmin):
    list_display = ('title', 'doctor', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'content')
