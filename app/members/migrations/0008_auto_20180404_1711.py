# Generated by Django 2.0.3 on 2018-04-04 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0007_user_phone_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='img_profile',
            field=models.ImageField(upload_to='user'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_num',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
