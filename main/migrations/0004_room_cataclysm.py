# Generated by Django 5.0.6 on 2024-06-07 08:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_room_bunker'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='cataclysm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.cataclysm'),
        ),
    ]
