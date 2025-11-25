from django.contrib import admin
from . models import GuestSession, WifiPlan
# Register your models here.

@admin.register(GuestSession)
class GuestSessionAdmin(admin.ModelAdmin):
    # specify the columns to see in the admin list
    list_display = ('mac_address', 'phone_number', 'plan', 'is_paid', 'created_at')

    list_filter = ('is_paid', 'created_at')
    search_fields = ('mac_address', 'phone_number')

@admin.register(WifiPlan)
class WifiPlan(admin.ModelAdmin):
    list_display = ('name_of_product', 'price', 'duration_in_minutes', 'data_limit_in_mbz')
