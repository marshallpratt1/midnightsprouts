# Generated by Django 4.1.7 on 2023-04-30 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automated_greenhouse', '0008_systemerror'),
    ]

    operations = [
        migrations.AddField(
            model_name='pumpstatus',
            name='frequency',
            field=models.IntegerField(default=0),
        ),
    ]
