# Generated by Django 4.2.6 on 2023-10-26 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_building_remove_switching_building'),
    ]

    operations = [
        migrations.AddField(
            model_name='switching',
            name='building',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='pages.building'),
        ),
    ]
