# Generated by Django 4.2.6 on 2023-10-28 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0014_alter_switching_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='switching',
            name='description',
        ),
    ]
