# Generated by Django 4.2.6 on 2023-12-10 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acsess_point', '0016_accesspoint_admin_password_accesspoint_admin_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesspoint',
            name='admin_password',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='accesspoint',
            name='admin_user',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='accesspoint',
            name='mac_address',
            field=models.CharField(max_length=25, unique=True),
        ),
        migrations.AlterField(
            model_name='accesspoint',
            name='wifi_password',
            field=models.CharField(max_length=50),
        ),
    ]