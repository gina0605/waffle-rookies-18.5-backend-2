# Generated by Django 3.1 on 2020-09-26 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seminar', '0006_auto_20200926_2334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userseminar',
            name='role',
            field=models.CharField(max_length=20),
        ),
    ]
