from django.db import models
import uuid
from apps.core.services.appwrite_service import AppwriteService


class Guest(models.Model):
    """
    Guest model represents a wedding guest with full personalization,
    RSVP states, preferences, multimedia content, and gamification.
    """

    # ------------------------
    # Identification / NFC
    # ------------------------
    id = models.AutoField(primary_key=True)  # Django default primary key
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # ------------------------
    # Personal Info
    # ------------------------
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], blank=True, null=True)

    # Renomeado de profile_picture_id para avatar_id
    avatar_id = models.CharField(max_length=100, blank=True, null=True)
    emoji = models.CharField(max_length=10, blank=True, null=True)

    # ------------------------
    # Recordações (Lista de imagens)
    # ------------------------
    memories = models.JSONField(default=list, blank=True, null=True)

    # ------------------------
    # Post-confirmation Preferences
    # ------------------------
    favorite_dish = models.CharField(max_length=100, blank=True, null=True)
    favorite_drink = models.CharField(max_length=100, blank=True, null=True)
    dietary_restrictions = models.CharField(max_length=200, blank=True, null=True)
    music_suggestion = models.CharField(max_length=200, blank=True, null=True)

    # Property renomeada
    @property
    def avatar_url(self):
        return AppwriteService.get_file_url(self.avatar_id)

    @property
    def memories_urls(self):
        """Retorna uma lista de URLs para as imagens de recordações"""
        if not self.memories:
            return []
        return [AppwriteService.get_file_url(image_id) for image_id in self.memories]

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''} ({self.token})"