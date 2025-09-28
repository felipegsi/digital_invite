from django.contrib import admin
from apps.guests.models import Guest

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'nickname', 'gender']
    search_fields = ['first_name', 'last_name', 'nickname']
    list_filter = ['gender']
    readonly_fields = ['token']