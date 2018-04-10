# Generated by Django 2.0.3 on 2018-04-09 22:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('house', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_date', models.DateField(unique=True)),
                ('check_out_date', models.DateField(unique=True)),
                ('guest_num', models.PositiveSmallIntegerField(blank=True, default=1)),
                ('bank_account', models.CharField(max_length=30)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('modified_date', models.DateField(auto_now=True)),
                ('payment_type', models.CharField(choices=[('DE', '무통장입금')], default='DE', max_length=2)),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='house.House')),
            ],
        ),
    ]
