# Generated by Django 2.0.3 on 2018-04-06 03:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('house', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='guest',
            field=models.ManyToManyField(blank=True, help_text='숙소를 예약한 게스트입니다.', related_name='reserved_houses', through='house.RelationWithHouseAndGuest', to=settings.AUTH_USER_MODEL, verbose_name='게스트'),
        ),
        migrations.AlterField(
            model_name='house',
            name='host',
            field=models.ForeignKey(help_text='숙소를 등록하는 호스트입니다.', on_delete=django.db.models.deletion.CASCADE, related_name='houses_with_host', to=settings.AUTH_USER_MODEL, verbose_name='호스트'),
        ),
    ]