# Generated by Django 4.1.7 on 2023-05-01 20:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('automated_greenhouse', '0012_gardenvalvestatus_frequency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gardenvalvestatus',
            name='next_start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='greenhouseplantervalvestatus',
            name='next_start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='greenhousetreevalvestatus',
            name='next_start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='pumpstatus',
            name='next_start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
