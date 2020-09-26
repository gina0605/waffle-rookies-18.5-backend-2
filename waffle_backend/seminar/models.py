from django.db import models
from django.contrib.auth.models import User


class Seminar(models.Model):
    name = models.CharField(unique=True, max_length=100)
    description = models.CharField(max_length=200, blank=True)
    start_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserSeminar(models.Model):
    user = models.ForeignKey(User, related_name='user_seminar', on_delete=models.CASCADE)
    seminar = models.ForeignKey(Seminar, related_name='user_seminar', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
