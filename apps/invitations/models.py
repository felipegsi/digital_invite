from django.db import models
import uuid
from django.utils import timezone
from apps.core.services.appwrite_service import AppwriteService
from apps.guests.models import Guest


class Invite(models.Model):
    # Relacionamento - um convidado pode ter vários convites
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name="invites"
    )

    # Dados básicos do convite
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    # Data de expiraçao
    expiration_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    # modelanaia para criarr evento
    created_at = models.DateTimeField(auto_now_add=True)

    # QR code também como ID do Appwrite(que devera ser gerado automticamente, logo nao deve aparecer no form)
    qr_code_id = models.CharField(max_length=100, blank=True, null=True)  # ID do arquivo no Appwrite

    # Status e interações
    invitation_status = models.CharField(max_length=20, choices=[('pending', 'Pendente'), ('accepted', 'Aceito'),
                                                                 ('declined', 'Recusado')], default='pending')
    response_date = models.DateTimeField(blank=True, null=True)
    last_access = models.DateTimeField(blank=True, null=True)
    interactions_count = models.IntegerField(default=0)

    # Conteúdo personalizado
    personalized_message = models.TextField(blank=True, null=True)
    pre_confirmation_video_url = models.URLField(blank=True, null=True)
    thank_you_video_url = models.URLField(blank=True, null=True)
    decline_reason = models.TextField(blank=True, null=True)

    def accept_invitation(self):
        from apps.gamification.models import Gamification  # importação local
        self.invitation_status = 'accepted'
        self.response_date = timezone.now()
        self.save()
        gamification, created = Gamification.objects.get_or_create(invite=self)
        if created:
            gamification.add_badge("first_acceptance")
            gamification.add_points(10)

    # Property renomeada
    @property
    def get_qr_code_url(self):
        return AppwriteService.get_file_url(self.qr_code_id)