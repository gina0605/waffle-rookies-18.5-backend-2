from django.db import models
from django.contrib.auth.models import User


class Seminar(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    capacity = models.PositiveSmallIntegerField()
    count = models.PositiveSmallIntegerField()
    time = models.TimeField()
    start_date = models.DateField(null=True)
    online = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserSeminar(models.Model):
    AVAILABLE_ROLES = ((0, 'participant'), (1, 'instructor'))
    user = models.ForeignKey(User, related_name='user_seminars', on_delete=models.CASCADE)
    seminar = models.ForeignKey(Seminar, related_name='user_seminars', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=20)
    dropped_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = [['user', 'seminar']]
