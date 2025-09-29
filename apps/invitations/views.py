import re
from io import BytesIO

from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.vary import vary_on_headers
from django.urls import reverse
from urllib.parse import urlencode

from apps.core.services.appwrite_service import AppwriteService
from apps.invitations.services.invite_service import InviteService
from apps.invitations.forms import InviteForm
from apps.invitations.models import Invite
from apps.guests.models import Guest

import qrcode
from qrcode.main import QRCode
from qrcode.image.svg import SvgImage
import json

@staff_member_required
def create_invite(request):
    """
    Cria um novo convite com QR code associado.
    """
    if request.method == "POST":
        return process_invite_form(request)
    else:
        return initialize_invite_form(request)

def initialize_invite_form(request):
    """
    Inicializa o formulário de convite com dados do convidado, se houver.
    """
    initial = {}
    guest_id = request.GET.get('guest')

    if guest_id and guest_id.isdigit():
        try:
            guest = get_object_or_404(Guest, pk=int(guest_id))
            initial['guest'] = guest
        except Http404:
            pass

    form = InviteForm(initial=initial)
    return render(request, "invitations/create_invite.html", {"form": form})

def process_invite_form(request):
    """
    Processa o formulário de convite quando submetido.
    """
    form = InviteForm(request.POST)
    if form.is_valid():
        invite = form.save(commit=False)

        # Gere o link para o QR Code
        link = generate_link(request, f"/invitations/detail/{invite.token}/")

        # Gera e faz upload do QR code
        invite.qr_code_id = generate_and_upload_qrcode(link, invite.token)

        invite.save()
        return redirect("invitations:invite_detail", token=invite.token)

    return render(request, "invitations/create_invite.html", {"form": form})

def generate_and_upload_qrcode(link, token):
    """
    Gera uma imagem QR code e faz upload para o Appwrite.
    Retorna o ID do arquivo no Appwrite.
    """
    import tempfile  # Use o módulo tempfile do Python padrão
    from django.core.files import File
    import os

    # Gera a imagem do QR code
    qr_image = generate_qr_code_image(link)

    # Convertendo a imagem PIL para arquivo temporário
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    qr_image.save(temp_file.name, format='PNG')
    temp_file.close()

    # Upload como arquivo Django
    qr_code_id = None
    try:
        with open(temp_file.name, 'rb') as f:
            django_file = File(f)
            django_file.name = f"qrcode_{token}.png"
            qr_code_id = AppwriteService.upload_file(django_file)
    finally:
        # Remove arquivo temporário
        os.unlink(temp_file.name)

    return qr_code_id

def generate_link(request,path):
    link = request.build_absolute_uri(path)

    return link

@vary_on_headers('User-Agent')
def invite_detail(request, token):
    """
    Exibe detalhes do convite com otimizações de performance e segurança
    """
    try:
        # Busca convite com cache e validação
        client_ip = get_client_ip(request)
        invite = InviteService.get_invite_with_cache(token, client_ip)
        
        # Valida acesso ao convite
        is_valid, error_message = InviteService.validate_invite_access(invite)
        if not is_valid:
            raise PermissionDenied(error_message)
        
        # Obtém URLs otimizadas das mídias
        media_data = InviteService.get_optimized_media_urls(invite.guest)
        # If there are no memories, use the avatar as a single splash slide as a graceful fallback
        if not media_data.get('memories_urls') or len(media_data.get('memories_urls')) == 0:
            if invite.guest and getattr(invite.guest, 'avatar_url', None):
                media_data['memories_urls'] = [invite.guest.avatar_url]
                # also provide a thumbnail copy
                media_data['memories_thumbnails'] = [invite.guest.avatar_url]

        # Determine whether we should auto-open the profile completion modal on page load
        should_show_profile_modal = False
        try:
            guest = invite.guest
            profile_incomplete = (not getattr(guest, 'dietary_restrictions', None)) or (not getattr(guest, 'music_suggestion', None))
            if invite.invitation_status == 'accepted' and profile_incomplete:
                should_show_profile_modal = True
        except Exception:
            should_show_profile_modal = False

        context = {
            'invite': invite,
            'media_data': media_data,
            'should_show_profile_modal': should_show_profile_modal,
        }
        
        return render(request, "invitations/invite_detail.html", context)
        
    except PermissionDenied as e:
        return render(request, "invitations/invite_expired.html", {
            'error_message': str(e)
        })
    except Exception as e:
        # Log do erro para debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao carregar convite {token}: {e}")
        
        return render(request, "invitations/invite_error.html", {
            'error_message': "Ocorreu um erro ao carregar o convite."
        })

def respond_invite(request, token):
    """
    Processa resposta RSVP do convidado com validações aprimoradas
    """
    invite = get_object_or_404(Invite, token=token, is_active=True)
    
    # Valida acesso
    is_valid, error_message = InviteService.validate_invite_access(invite)
    if not is_valid:
        raise PermissionDenied(error_message)
    
    if request.method == "POST":
        status = request.POST.get('invitation_status')
        decline_reason = request.POST.get('decline_reason', '').strip()
        
        # Processa resposta usando o service
        success, message = InviteService.process_rsvp_response(
            invite, status, decline_reason
        )
        
        if success:
            # If accepted, and guest profile incomplete, redirect with a flag to open profile modal
            redirect_url = reverse('invitations:invite_detail', kwargs={'token': token})
            if status == 'accepted':
                guest = invite.guest
                profile_incomplete = (not getattr(guest, 'dietary_restrictions', None)) or (not getattr(guest, 'music_suggestion', None))
                if profile_incomplete:
                    redirect_url = f"{redirect_url}?{urlencode({'profile_modal': '1'})}"
            return redirect(redirect_url)
        else:
            # Retorna erro se processamento falhou
            return render(request, "invitations/invite_detail.html", {
                'invite': invite,
                'error_message': message,
                'media_data': InviteService.get_optimized_media_urls(invite.guest)
            })
    
    return render(request, "invitations/invite_detail.html", {
        'invite': invite,
        'media_data': InviteService.get_optimized_media_urls(invite.guest)
    })

def get_client_ip(request):
    """
    Obtém o IP real do cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def generate_qr_code_image(link):
    """Gera um QR code em formato PNG para o link fornecido e retorna o objeto de imagem"""
    qr = QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img

def generate_qr_code_vector(link):
    qr = QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(image_factory=SvgImage)

    buffer = BytesIO()
    img.save(buffer)
    svg = buffer.getvalue().decode("utf-8")

    # Remove declaração XML
    svg = re.sub(r'^\s*<\?xml[^>]*>\s*', '', svg)
    svg = re.sub(r'\s+xmlns:svg="[^"]+"', '', svg)
    svg = re.sub(r'<(/?)svg:', r'<\1', svg)
    svg = re.sub(r'([0-9]+(?:\.[0-9]+)?)mm', r'\1', svg)

    # Adiciona fill="black" em todos os <rect>
    svg = re.sub(r'<rect\b([^>]*)>', r'<rect\1 fill="black">', svg)

    wh_match = re.search(r'<svg[^>]*\bwidth="([\d\.]+)(?:mm|px)?"[^>]*\bheight="([\d\.]+)(?:mm|px)?"[^>]*>', svg)
    open_tag_match = re.search(r'<svg[^>]*>', svg)
    if open_tag_match:
        if wh_match:
            w = float(wh_match.group(1))
            h = float(wh_match.group(2))
        else:
            w = h = 200.0
        new_tag = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(w)} {int(h)}" width="200" height="200">'
        svg = svg[:open_tag_match.start()] + new_tag + svg[open_tag_match.end():]
    else:
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">{svg}</svg>'

    return mark_safe(svg)

def complete_profile(request, token):
    """
    Endpoint to complete guest profile after RSVP accept.
    Expects JSON body: { dietary, music, gender }
    Maps gender ('male'|'female'|'other'|'') to Guest.gender ('M'|'F'|None).
    Returns JSON response.
    """
    try:
        invite = get_object_or_404(Invite, token=token, is_active=True)

        # Validate access
        is_valid, error_message = InviteService.validate_invite_access(invite)
        if not is_valid:
            return JsonResponse({'success': False, 'error': str(error_message)}, status=403)

        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

        # Parse JSON body
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        dietary = payload.get('dietary')
        music = payload.get('music')
        gender_in = (payload.get('gender') or '').lower()

        # Map gender to Guest.gender choices
        if gender_in == 'male' or gender_in == 'm':
            gender_val = 'M'
        elif gender_in == 'female' or gender_in == 'f':
            gender_val = 'F'
        else:
            gender_val = None

        guest = invite.guest

        if dietary is not None:
            guest.dietary_restrictions = dietary.strip()[:200]
        if music is not None:
            guest.music_suggestion = music.strip()[:200]
        # Update gender only if provided
        if gender_in != '':
            guest.gender = gender_val

        guest.save()

        return JsonResponse({'success': True})

    except Http404:
        return JsonResponse({'success': False, 'error': 'Invite not found'}, status=404)
    except PermissionDenied as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=403)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error saving profile')
        return JsonResponse({'success': False, 'error': 'Server error'}, status=500)
