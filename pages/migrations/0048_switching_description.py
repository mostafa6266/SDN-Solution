# Generated by Django 4.2.6 on 2023-12-01 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0047_alter_switching_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='switching',
            name='description',
            field=models.CharField(default='acsess', max_length=50, null=True),
        ),
    ]
