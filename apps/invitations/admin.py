from django.contrib import admin
from apps.invitations.models import Invite

@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ['guest', 'invitation_status', 'created_at']
    list_filter = ['invitation_status']
    search_fields = ['guest__first_name', 'guest__last_name', 'personalized_message']
    date_hierarchy = 'created_at'
    readonly_fields = ['token', 'created_at', 'interactions_count', 'response_date', 'last_access']
