# Generated by Django 5.1.2 on 2024-11-15 20:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noivos', '0005_presentes_link_sugestao_compra_alter_presentes_foto_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presentes',
            name='reservado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='noivos.convidados'),
        ),
    ]
