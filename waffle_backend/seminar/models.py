from django.db import models


class Seminar(models.Model):
    name = models.CharField(unique=True, max_length=100)
    description = models.CharField(max_length=200, blank=True)
    start_date = models.DateField(null=True)

