# Generated by Django 4.2.6 on 2023-12-10 07:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0051_building_ip_range'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='building',
            name='ip_range',
        ),
    ]
