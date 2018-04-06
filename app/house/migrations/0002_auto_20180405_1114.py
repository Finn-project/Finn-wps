# Generated by Django 2.0.3 on 2018-04-05 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('house', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='house_type',
            field=models.CharField(choices=[('AP', '아파트'), ('HO', '주택'), ('OR', '원룸')], default='HO', help_text='숙소를 선택 하세요. 디비에는 AP HO OR 등으로 저장.(기본값은 주택)', max_length=2, verbose_name='숙소 타입'),
        ),
        migrations.AlterField(
            model_name='house',
            name='maximum_check_in_duration',
            field=models.PositiveSmallIntegerField(blank=True, default=3, help_text='체크인 할 수 있는 최대 기간을 입력 하세요. (기본값은 3=3박4일)', verbose_name='최대 체크인 기간'),
        ),
        migrations.AlterField(
            model_name='house',
            name='minimum_check_in_duration',
            field=models.PositiveSmallIntegerField(blank=True, default=1, help_text='체크인 할 수 있는 최소 기간을 입력 하세요. (기본값은 1=1박2일)', verbose_name='최소 체크인 기간'),
        ),
    ]