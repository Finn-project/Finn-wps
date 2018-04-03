from django.db import models


class House(models.Model):
    ROOM_TYPE_APARTMENT = 'AP'
    ROOM_TYPE_HOUSING = 'HO'
    ROOM_TYPE_ONEROOM = 'OR'

    ROOM_TYPE_CHOICES = (
        (ROOM_TYPE_APARTMENT, '아파트'),
        (ROOM_TYPE_HOUSING, '주택'),
        (ROOM_TYPE_ONEROOM, '원룸'),
    )

    room_type = models.CharField(max_length=2, choices=ROOM_TYPE_CHOICES, default=ROOM_TYPE_HOUSING)
    personnel = models.SmallIntegerField()
