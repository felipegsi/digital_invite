from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def get_video_embed_url(url):
    """
    Converte URLs de vídeo para formato embed
    """
    if not url:
        return ""
    
    # YouTube
    if 'youtube.com/watch' in url:
        video_id = url.split('v=')[1].split('&')[0]
        return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
        return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
    
    # Vimeo
    elif 'vimeo.com/' in url:
        video_id = url.split('vimeo.com/')[1].split('?')[0]
        return f"https://player.vimeo.com/video/{video_id}"
    
    return url

@register.filter
def json_script_safe(value):
    """
    Converte valor para JSON seguro para uso em scripts
    """
    return mark_safe(json.dumps(value))

@register.inclusion_tag('invitations/components/memory_gallery.html')
def memory_gallery(memories_data):
    """
    Renderiza galeria de memórias
    """
    return {'memories_data': memories_data}

@register.inclusion_tag('invitations/components/rsvp_form.html')
def rsvp_form(invite):
    """
    Renderiza formulário RSVP
    """
    return {'invite': invite}