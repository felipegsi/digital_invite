import json
import logging
import os

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.vary import vary_on_headers
from django.urls import reverse
from django.http import JsonResponse, Http404

from apps.core.services.appwrite_service import AppwriteService
from apps.invitations.services.invite_service import InviteService
from apps.invitations.forms import InviteForm
from apps.invitations.models import Invite
from apps.guests.models import Guest

import qrcode
from qrcode.main import QRCode

logger = logging.getLogger(__name__)


def generate_link(request, path):
    """Gera URL absoluta a partir do path relativo fornecido."""
    return request.build_absolute_uri(path)


def generate_qr_code_image(link):
    """Gera um QR code em formato PNG para o link fornecido e retorna o objeto de imagem PIL."""
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


def generate_and_upload_qrcode(link, token):
    """Gera um QR code PNG e faz upload usando o AppwriteService; retorna o file id."""
    import tempfile
    from django.core.files import File

    qr_image = generate_qr_code_image(link)

    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    try:
        qr_image.save(temp_file.name, format='PNG')
        temp_file.close()
        with open(temp_file.name, 'rb') as f:
            django_file = File(f)
            django_file.name = f"qrcode_{token}.png"
            qr_code_id = AppwriteService.upload_file(django_file)
    finally:
        try:
            os.unlink(temp_file.name)
        except Exception:
            pass

    return qr_code_id


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def create_invite(request):
    """Cria um novo convite (área administrativa)."""
    # Mantido simples; decorator de staff aplicado via URL ou admin
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            invite = form.save(commit=False)
            link = generate_link(request, f"/invitations/detail/{invite.token}/")
            invite.qr_code_id = generate_and_upload_qrcode(link, invite.token)
            invite.save()
            return redirect('invitations:invite_detail', token=invite.token)
        return render(request, 'invitations/create_invite.html', {'form': form})

    guest_id = request.GET.get('guest')
    initial = {}
    if guest_id and guest_id.isdigit():
        try:
            initial['guest'] = get_object_or_404(Guest, pk=int(guest_id))
        except Http404:
            pass
    form = InviteForm(initial=initial)
    return render(request, 'invitations/create_invite.html', {'form': form})


@vary_on_headers('User-Agent')
def invite_detail(request, token):
    """Renderiza a página de detalhes do convite com dados de mídia e sinalização para abrir modal de perfil."""
    try:
        client_ip = get_client_ip(request)
        invite = InviteService.get_invite_with_cache(token, client_ip)

        is_valid, error_message = InviteService.validate_invite_access(invite)
        if not is_valid:
            raise PermissionDenied(error_message)

        media_data = InviteService.get_optimized_media_urls(invite.guest)
        if not media_data.get('memories_urls'):
            if invite.guest and getattr(invite.guest, 'avatar_url', None):
                media_data['memories_urls'] = [invite.guest.avatar_url]
                media_data['memories_thumbnails'] = [invite.guest.avatar_url]

        should_show_profile_modal = False
        try:
            guest = invite.guest
            profile_incomplete = (not getattr(guest, 'dietary_restrictions', None)) or (not getattr(guest, 'music_suggestion', None))
            if invite.invitation_status == 'accepted' and profile_incomplete:
                should_show_profile_modal = True
        except Exception:
            should_show_profile_modal = False

        # Allow forcing modal via query param (respond_invite redirects with ?profile_modal=1)
        if request.GET.get('profile_modal') in ('1', 'true', 'yes'):
            should_show_profile_modal = True

        return render(request, 'invitations/invite_detail.html', {
            'invite': invite,
            'media_data': media_data,
            'should_show_profile_modal': should_show_profile_modal,
        })

    except PermissionDenied as e:
        return render(request, 'invitations/invite_expired.html', {'error_message': str(e)})
    except Exception:
        logger.exception('Erro ao carregar convite %s', token)
        return render(request, 'invitations/invite_error.html', {'error_message': 'Ocorreu um erro ao carregar o convite.'})


def respond_invite(request, token):
    invite = get_object_or_404(Invite, token=token, is_active=True)

    is_valid, error_message = InviteService.validate_invite_access(invite)
    if not is_valid:
        raise PermissionDenied(error_message)

    if request.method == 'POST':
        status = request.POST.get('invitation_status')
        decline_reason = request.POST.get('decline_reason', '').strip()

        success, message = InviteService.process_rsvp_response(invite, status, decline_reason)

        if success:
            redirect_url = reverse('invitations:invite_detail', kwargs={'token': token})
            if status == 'accepted':
                guest = invite.guest
                profile_incomplete = (not getattr(guest, 'dietary_restrictions', None)) or (not getattr(guest, 'music_suggestion', None))
                if profile_incomplete:
                    redirect_url = f"{redirect_url}?profile_modal=1"
            return redirect(redirect_url)

        return render(request, 'invitations/invite_detail.html', {
            'invite': invite,
            'error_message': message,
            'media_data': InviteService.get_optimized_media_urls(invite.guest)
        })

    return render(request, 'invitations/invite_detail.html', {
        'invite': invite,
        'media_data': InviteService.get_optimized_media_urls(invite.guest)
    })


def complete_profile(request, token):
    try:
        invite = get_object_or_404(Invite, token=token, is_active=True)

        is_valid, error_message = InviteService.validate_invite_access(invite)
        if not is_valid:
            return JsonResponse({'success': False, 'error': str(error_message)}, status=403)

        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        dietary = payload.get('dietary')
        music = payload.get('music')
        gender_in = (payload.get('gender') or '').lower()

        if gender_in in ('male', 'm'):
            gender_val = 'M'
        elif gender_in in ('female', 'f'):
            gender_val = 'F'
        else:
            gender_val = None

        guest = invite.guest
        if dietary is not None:
            guest.dietary_restrictions = dietary.strip()[:200]
        if music is not None:
            guest.music_suggestion = music.strip()[:200]
        if gender_in != '':
            guest.gender = gender_val

        guest.save()
        return JsonResponse({'success': True})

    except Http404:
        return JsonResponse({'success': False, 'error': 'Invite not found'}, status=404)
    except PermissionDenied as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=403)
    except Exception:
        logger.exception('Error saving profile')
        return JsonResponse({'success': False, 'error': 'Server error'}, status=500)
