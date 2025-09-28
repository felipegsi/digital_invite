from django import forms
from apps.invitations.models import Invite
from apps.guests.models import Guest

class InviteForm(forms.ModelForm):
    guest = forms.ModelChoiceField(queryset=Guest.objects.all())
    expiration_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial='2026-04-11T12:00'
    )

    class Meta:
        model = Invite
        fields = [
            'guest',
            'expiration_date',
            'personalized_message',
            'pre_confirmation_video_url',
            'thank_you_video_url',
        ]
