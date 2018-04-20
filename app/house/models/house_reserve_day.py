from django.db import models

__all__ = (
    'HouseReserveDay',
)


class HouseReserveDay(models.Model):
    date = models.DateField(
        verbose_name='예약된 날',
        help_text='예약된 날 입니다.',

        unique=True,
    )
