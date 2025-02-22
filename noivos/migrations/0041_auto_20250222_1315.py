# -*- coding: utf-8 -*-
from django.db import migrations, models

def add_tipo_column(apps, schema_editor):
    ImagemNoivos = apps.get_model('noivos', 'ImagemNoivos')
    schema_editor.add_field(
        ImagemNoivos,
        models.CharField(max_length=10, choices=[('noiva', 'Noiva'), ('noivo', 'Noivo')])
    )

class Migration(migrations.Migration):

    dependencies = [
        ('noivos', '0040_imagemnoivos'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagemnoivos',
            name='tipo',
            field=models.CharField(max_length=10, choices=[('noiva', 'Noiva'), ('noivo', 'Noivo')]),
        ),
    ]
