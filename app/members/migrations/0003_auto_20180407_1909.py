# Generated by Django 2.0.3 on 2018-04-07 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_auto_20180407_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_email_user',
            field=models.BooleanField(default=False),
        ),
    ]
