from django.db import models
from apps.invitations.models import Invite

# Create your models here.
class Gamification(models.Model):
    invite = models.OneToOneField(
        Invite,
        on_delete=models.CASCADE,
        related_name="gamification"
    )

    points = models.IntegerField(default=0)
    badges = models.JSONField(default=list, blank=True)
    completed_missions = models.JSONField(default=list, blank=True)
    secret_missions = models.JSONField(default=list, blank=True)
    rank = models.IntegerField(blank=True, null=True)

    def add_points(self, amount):
        self.points += amount
        self.save()

    def spend_points(self, amount):
        if self.points >= amount:
            self.points -= amount
            self.save()
            return True
        return False

    def add_badge(self, badge_name):
        if not self.badges:
            self.badges = []
        if badge_name not in self.badges:
            self.badges.append(badge_name)
            self.save()

    def complete_mission(self, mission_name):
        if not self.completed_missions:
            self.completed_missions = []
        if mission_name not in self.completed_missions:
            self.completed_missions.append(mission_name)
            self.save()

    def unlock_secret_mission(self, mission_name):
        if not self.secret_missions:
            self.secret_missions = []
        if mission_name not in self.secret_missions:
            self.secret_missions.append(mission_name)
            self.save()
