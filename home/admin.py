from django.contrib import admin
from .models import AirQuality, UserInfo
from django.contrib.auth.admin import UserAdmin


# Register your models here.

@admin.register(AirQuality)
class AirQualityAdmin(admin.ModelAdmin):
    list_display = ('city', 'date', 'airQuality', 'AQI', 'PM', 'PM10', 'So2', 'rank')
    search_fields = ('city', 'date', 'airQuality')
    list_filter = ('city', 'airQuality', 'year', 'month')
    list_per_page = 20
    ordering = ('-date',)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'created_at')
    list_per_page = 20

admin.site.register(UserInfo,CustomUserAdmin)