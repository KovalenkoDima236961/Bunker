# Generated by Django 5.0.6 on 2024-06-06 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cataclysm',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('year', models.IntegerField()),
                ('description', models.CharField(max_length=400)),
                ('how_many_time_do_you_have', models.CharField(max_length=100)),
                ('remaining_population', models.CharField(max_length=150)),
            ],
        ),
    ]
