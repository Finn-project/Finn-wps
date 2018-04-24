from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from ..models import dynamic_img_house_path
from .managers import HouseImageManager
from ..models.house import House

__all__ = (
    'HouseImage',
)


class HouseImage(models.Model):
    """
    HouseImage모델은  House모델을 참조 하며
    House모델이 지워지면 연결된 HouseImage모델도 지워 진다.
    """
    image = models.ImageField(
        verbose_name='숙소 이미지',
        help_text='숙소와 연결된 이미지를 저장합니다.',

        upload_to=dynamic_img_house_path,
    )
    house = models.ForeignKey(
        House,

        verbose_name='숙소',
        help_text='이미지와 연결된 숙소를 저장합니다.',

        related_name='images',
        on_delete=models.CASCADE,
    )

    objects = HouseImageManager()

    class Meta:
        verbose_name_plural = '숙소 이미지들'

    def __str__(self):
        return f'[house|{self.house.pk}] {self.image.name}'


@receiver(pre_delete, sender=HouseImage)
def remove_house_image_s3storage(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete()
