from django.db import models

__all__ = (
    'HouseReserveDay',
)


class HouseReserveDay(models.Model):
    date = models.DateField(
        verbose_name='쉬는날',
        help_text='쉬는날을 입력해 주세요',

        unique=True,
    )
