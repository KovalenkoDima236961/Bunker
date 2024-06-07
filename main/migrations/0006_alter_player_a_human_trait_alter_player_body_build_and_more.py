# Generated by Django 5.0.6 on 2024-06-07 08:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_room_is_game_started'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='a_human_trait',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.humantrait'),
        ),
        migrations.AlterField(
            model_name='player',
            name='body_build',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.bodybuild'),
        ),
        migrations.AlterField(
            model_name='player',
            name='gender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.gender'),
        ),
        migrations.AlterField(
            model_name='player',
            name='health',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.health'),
        ),
        migrations.AlterField(
            model_name='player',
            name='hobby',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.hobby'),
        ),
        migrations.AlterField(
            model_name='player',
            name='inventory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.inventory'),
        ),
        migrations.AlterField(
            model_name='player',
            name='more_information',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.moreinformation'),
        ),
        migrations.AlterField(
            model_name='player',
            name='phobia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.phobia'),
        ),
        migrations.AlterField(
            model_name='player',
            name='special_feature1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='special_feature1_players', to='main.specialfeature'),
        ),
        migrations.AlterField(
            model_name='player',
            name='special_feature2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='special_feature2_players', to='main.specialfeature'),
        ),
        migrations.AlterField(
            model_name='player',
            name='speciality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.speciality'),
        ),
    ]
