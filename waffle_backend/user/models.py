from django.db import models
from django.contrib.auth.models import User


class ParticipantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='participant')
    university = models.CharField(max_length=50, blank=True)
    accepted = models.BooleanField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='instructor')
    company = models.CharField(max_length=50, blank=True)
    year = models.PositiveSmallIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
