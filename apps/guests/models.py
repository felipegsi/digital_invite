from django.db import models
import uuid
from apps.core.services.appwrite_service import AppwriteService


class Guest(models.Model):
    """Modelo do convidado com campos principais e helpers para URLs de mídia."""

    id = models.AutoField(primary_key=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], blank=True, null=True)

    avatar_id = models.CharField(max_length=100, blank=True, null=True)
    emoji = models.CharField(max_length=10, blank=True, null=True)

    memories = models.JSONField(default=list, blank=True, null=True)

    favorite_dish = models.CharField(max_length=100, blank=True, null=True)
    favorite_drink = models.CharField(max_length=100, blank=True, null=True)
    dietary_restrictions = models.CharField(max_length=200, blank=True, null=True)
    music_suggestion = models.CharField(max_length=200, blank=True, null=True)

    @property
    def avatar_url(self):
        """Retorna URL do avatar via AppwriteService (ou None)."""
        return AppwriteService.get_file_url(self.avatar_id)

    @property
    def memories_urls(self):
        """Retorna lista de URLs das memórias (padrão: lista vazia)."""
        if not self.memories:
            return []
        return [AppwriteService.get_file_url(image_id) for image_id in self.memories if image_id]

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''} ({self.token})"