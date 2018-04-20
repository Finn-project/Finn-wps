from django.db import models

from .managers import HouseDisableDayManager

__all__ = (
    'HouseDisableDay',
)


class HouseDisableDay(models.Model):
    date = models.DateField(
        verbose_name='쉬는날',
        help_text='쉬는날을 입력해 주세요',

        # manytomany로 하기 때문에 같은날이 존재 x
        unique=True,
    )

    objects = HouseDisableDayManager()
