from django.shortcuts import render, redirect, get_object_or_404
from apps.gamification.models import Gamification
from apps.invitations.models import Invite

def leaderboard(request):
    """
    Exibe o ranking dos convidados por pontos
    """
    gamifications = Gamification.objects.all().order_by('-points')[:20]
    return render(request, "gamification/leaderboard.html", {"gamifications": gamifications})

def user_achievements(request, token):
    """
    Mostra as conquistas do convidado
    """
    invite = get_object_or_404(Invite, token=token)
    try:
        gamification = invite.gamification
        return render(request, "gamification/achievements.html", {
            "invite": invite,
            "gamification": gamification
        })
    except Gamification.DoesNotExist:
        return redirect("invite_detail", token=token)
