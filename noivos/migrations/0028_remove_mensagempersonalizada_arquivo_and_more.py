# Generated by Django 5.1.3 on 2024-12-27 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noivos', '0027_mensagempersonalizada_arquivo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mensagempersonalizada',
            name='arquivo',
        ),
        migrations.AddField(
            model_name='mensagempersonalizada',
            name='arquivo_base64',
            field=models.TextField(blank=True, null=True),
        ),
    ]
