from django.contrib import admin
from apps.gamification.models import Gamification


@admin.register(Gamification)
class GamificationAdmin(admin.ModelAdmin):
    list_display = ['invite', 'points', 'rank', 'get_guest_name']
    search_fields = ['invite__guest__first_name', 'invite__guest__last_name']
    list_filter = ['rank']
    readonly_fields = ['badges', 'completed_missions', 'secret_missions']

    def get_guest_name(self, obj):
        return f"{obj.invite.guest.first_name} {obj.invite.guest.last_name or ''}"

    get_guest_name.short_description = 'Convidado'
