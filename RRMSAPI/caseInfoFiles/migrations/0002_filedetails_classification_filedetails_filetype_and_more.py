# Generated by Django 5.1.7 on 2025-04-08 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caseInfoFiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='filedetails',
            name='classification',
            field=models.TextField(default='private', max_length=200),
        ),
        migrations.AddField(
            model_name='filedetails',
            name='fileType',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='filedetails',
            name='hashTag',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='filedetails',
            name='subject',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
