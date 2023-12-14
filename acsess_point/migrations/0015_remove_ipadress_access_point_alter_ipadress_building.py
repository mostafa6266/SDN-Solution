# Generated by Django 4.2.6 on 2023-12-10 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0052_remove_building_ip_range'),
        ('acsess_point', '0014_ipadress_access_point'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ipadress',
            name='access_point',
        ),
        migrations.AlterField(
            model_name='ipadress',
            name='building',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ip_address', to='pages.building'),
        ),
    ]