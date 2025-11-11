from django.contrib import admin
from . models import GuestSession
# Register your models here.

@admin.register(GuestSession)
class GuestSessionAdmin(admin.ModelAdmin):
    # specify the columns to see in the admin list
    list_display = ('mac_address', 'phone_number', 'is_paid', 'created_at')

    list_filter = ('is_paid', 'created_at')
