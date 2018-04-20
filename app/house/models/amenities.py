from django.db import models

__all__ = (
    'Amenities',
)


class Amenities(models.Model):
    """
    House와 연결된 편의 물품
    """
    name = models.CharField(
        help_text='100자 까지의 물건의 이름을 저장 합니다.',

        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name_plural = '편의 물품'

    def __str__(self):
        return self.name
