# Generated by Django 3.1 on 2020-10-08 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20200927_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participantprofile',
            name='accepted',
            field=models.BooleanField(default=True),
        ),
    ]
