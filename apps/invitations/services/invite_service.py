from django.core.cache import cache
from django.utils import timezone
from django.shortcuts import get_object_or_404
from apps.invitations.models import Invite
from apps.core.services.appwrite_service import AppwriteService
import logging

logger = logging.getLogger(__name__)

class InviteService:
    """
    Serviço para gerenciar lógica de negócio dos convites
    """
    
    @staticmethod
    def get_invite_with_cache(token, request_ip=None):
        """
        Busca convite com cache e registra acesso
        """
        cache_key = f"invite_{token}"
        invite = cache.get(cache_key)
        
        if not invite:
            invite = get_object_or_404(Invite, token=token, is_active=True)
            # Cache por 15 minutos
            cache.set(cache_key, invite, 900)
        
        # Registra acesso (sem cache para estatísticas precisas)
        InviteService._register_access(invite, request_ip)
        
        return invite
    
    @staticmethod
    def _register_access(invite, request_ip=None):
        """
        Registra acesso ao convite
        """
        try:
            invite.last_access = timezone.now()
            invite.interactions_count += 1
            invite.save(update_fields=['last_access', 'interactions_count'])
        except Exception as e:
            logger.warning(f"Erro ao registrar acesso para convite {invite.token}: {e}")
    
    @staticmethod
    def get_optimized_media_urls(guest):
        """
        Retorna URLs otimizadas das mídias do convidado
        """
        media_data = {
            'avatar_url': None,
            'memories_urls': [],
            'memories_thumbnails': []
        }
        
        # Avatar otimizado
        if guest.avatar_id:
            media_data['avatar_url'] = AppwriteService.get_file_url(guest.avatar_id)
        
        # Memórias com thumbnails
        if guest.memories:
            for memory_id in guest.memories:
                full_url = AppwriteService.get_file_url(memory_id)
                if full_url:
                    media_data['memories_urls'].append(full_url)
                    # Para thumbnails, você pode implementar redimensionamento no Appwrite
                    # ou usar parâmetros de query para otimização
                    thumbnail_url = f"{full_url}&width=300&height=300&quality=80"
                    media_data['memories_thumbnails'].append(thumbnail_url)
        
        return media_data
    
    @staticmethod
    def validate_invite_access(invite):
        """
        Valida se o convite pode ser acessado
        """
        if not invite.is_active:
            return False, "Convite não está ativo"
        
        if invite.expiration_date and invite.expiration_date < timezone.now():
            return False, "Convite expirado"
        
        return True, None
    
    @staticmethod
    def process_rsvp_response(invite, status, decline_reason=None):
        """
        Processa resposta RSVP do convidado
        """
        if status not in ['accepted', 'declined']:
            return False, "Status inválido"
        
        invite.invitation_status = status
        invite.response_date = timezone.now()
        
        if status == 'declined' and decline_reason:
            invite.decline_reason = decline_reason
        
        invite.save()
        
        # Processa gamificação se aceito
        if status == 'accepted':
            invite.accept_invitation()
        
        # Limpa cache
        cache_key = f"invite_{invite.token}"
        cache.delete(cache_key)
        
        return True, "Resposta processada com sucesso"