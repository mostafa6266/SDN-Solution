# Generated by Django 4.2.6 on 2023-11-19 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0042_switching_mac_addresses_delete_macaddresstable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='switching',
            name='mac_addresses',
        ),
        migrations.AddField(
            model_name='switching',
            name='mac_addresses_tables',
            field=models.TextField(blank=True, null=True),
        ),
    ]
