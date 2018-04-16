from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill

from utils.image.resize import clear_imagekit_cache

__all__ = (
    'House',
    'HouseDisableDay',
    'HouseImage',
    'Amenities',
    'Facilities',
)


def dynamic_img_cover_path(instance, file_name):
    return f'house/user_{instance.host.id}/house_{instance.pk}/{file_name}'


def dynamic_img_house_path(instance, file_name):
    return f'house/user_{instance.house.host.id}/house_{instance.house.pk}/images/{file_name}'


class House(models.Model):
    HOUSE_TYPE_APARTMENT = 'AP'
    HOUSE_TYPE_HOUSING = 'HO'
    HOUSE_TYPE_ONEROOM = 'OR'

    HOUSE_TYPE_CHOICES = (
        (HOUSE_TYPE_APARTMENT, '아파트'),
        (HOUSE_TYPE_HOUSING, '주택'),
        (HOUSE_TYPE_ONEROOM, '원룸'),
    )

    house_type = models.CharField(
        verbose_name='숙소 타입',
        help_text='숙소를 선택 하세요. 디비에는 AP HO OR 등으로 저장.(기본값은 주택)',

        max_length=2,
        choices=HOUSE_TYPE_CHOICES,
        default=HOUSE_TYPE_HOUSING
    )
    name = models.CharField(
        verbose_name='숙소 이름',
        help_text='숙소의 이름을 입력하세요.',

        max_length=100,
    )
    description = models.TextField(
        verbose_name='숙소 설명',
        help_text='숙소를 설명 하세요.',
    )

    room = models.PositiveSmallIntegerField(
        verbose_name='방 수',
        help_text='방 수를 입력 하세요.',
    )
    bed = models.PositiveSmallIntegerField(
        verbose_name='침대 수',
        help_text='침대 수를 입력 하세요.',
    )
    bathroom = models.PositiveSmallIntegerField(
        verbose_name='욕실 수',
        help_text='욕실 수를 입력 하세요.',
    )

    personnel = models.PositiveSmallIntegerField(
        verbose_name='숙박 인원',
        help_text='숙박 인원 입력 하세요.',
    )

    amenities = models.ManyToManyField(
        'Amenities',

        verbose_name='편의 물품',
        help_text='편의 물품의 종류를 선택하세요.',

        related_name='houses_with_amenities',
        blank=True,
    )

    facilities = models.ManyToManyField(
        'Facilities',

        verbose_name='편의 시설',
        help_text='편의 시설을 선택하세요.',

        related_name='houses_with_facilities',
        blank=True,
    )

    minimum_check_in_duration = models.PositiveSmallIntegerField(
        verbose_name='최소 체크인 기간',
        help_text='체크인 할 수 있는 최소 기간을 입력 하세요.',
    )
    maximum_check_in_duration = models.PositiveSmallIntegerField(
        verbose_name='최대 체크인 기간',
        help_text='체크인 할 수 있는 최대 기간을 입력 하세요.',
    )

    maximum_check_in_range = models.PositiveSmallIntegerField(
        verbose_name='체크인 가능한 한계 시간',
        help_text='오늘을 기준으로 체크인이 가능한 날 수 적어주세요',
    )

    price_per_night = models.PositiveIntegerField(
        verbose_name='하루 요금',
        help_text='하루 요금을 적어 주세요.',
    )

    created_date = models.DateField(
        verbose_name='등록일',
        help_text='날짜로 입력 가능 합니다.(기본값은 오늘)',

        auto_now_add=True,
    )
    modified_date = models.DateField(
        verbose_name='수정일',
        help_text='날짜로 입력 가능 합니다.(기본값은 오늘)',

        auto_now=True
    )

    disable_days = models.ManyToManyField(
        'HouseDisableDay',

        verbose_name='쉬는날',
        help_text='쉬는날을 선택하세요.',

        related_name='houses_with_disable_day',
        blank=True,
    )

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,

        verbose_name='호스트',
        help_text='숙소를 등록하는 호스트입니다.',

        related_name='houses_with_host',
        on_delete=models.CASCADE,
    )

    country = models.CharField(
        verbose_name='국가',
        help_text='특별시/광역시/도 을 입력 하세요 (서울특별시)',

        max_length=100,

        blank=True,
    )

    city = models.CharField(
        verbose_name='시/도',
        help_text='특별시/광역시/도 을 입력 하세요 (서울특별시)',

        max_length=100,

        blank=True,
    )
    district = models.CharField(
        verbose_name='시/군/구',
        help_text='시/군/구 를 입력 하세요 (관악구)',

        max_length=100,

        blank=True,
    )
    dong = models.CharField(
        verbose_name='동/읍/면',
        help_text='상세 주소를 입력 하세요 (신림동)',

        max_length=100,

        blank=True,
    )
    address1 = models.CharField(
        verbose_name='상세 주소1',
        help_text='상세 주소1을 입력 하세요 (790-2)',

        max_length=100,

        blank=True,
    )
    # address2 = models.CharField(
    #     verbose_name='상세 주소2',
    #     help_text='상세 주소2를 입력 하세요 (희망빌라 2차 201호)',
    #
    #     max_length=100,
    #
    #     blank=True,
    # )
    latitude = models.DecimalField(
        verbose_name='위도',
        help_text='위도를 소수점(7자리) 입력 가능 (xx.1234567)',

        decimal_places=7,
        max_digits=9
    )
    longitude = models.DecimalField(
        verbose_name='경도',
        help_text='경도를 소수점(7자리) 입력 가능 (xxx.1234567)',

        decimal_places=7,
        max_digits=10
    )

    img_cover = models.ImageField(upload_to=dynamic_img_cover_path, blank=True, default='')

    img_cover_thumbnail = ImageSpecField(
        source='img_cover',
        processors=[ResizeToFill(400, 300)],
        format='png',
        options={'quality': 100}
    )

    class Meta:
        verbose_name_plural = '숙소'

    def __str__(self):
        return self.name


class HouseDisableDay(models.Model):
    date = models.DateField(
        verbose_name='쉬는날',
        help_text='쉬는날을 입력해 주세요',

        # manytomany로 하기 때문에 같은날이 존재 x
        unique=True,
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

    class Meta:
        verbose_name_plural = '숙소 이미지들'

    def __str__(self):
        return f'{self.image.name}'

    def __unicode__(self):
        return f'{self.image.name}'


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


class Facilities(models.Model):
    """
    House와 연결된 편의 시설
    """
    name = models.CharField(
        help_text='100자 까지의 물건의 이름을 저장 합니다.',

        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name_plural = '편의 시설'

    def __str__(self):
        return self.name


@receiver(pre_delete, sender=House)
def remove_file_from_storage(sender, instance, **kwargs):
    clear_imagekit_cache()
    if instance.img_cover:
        instance.img_cover.delete()

    if instance.images:
        for house_image in instance.images.all():
            if house_image.image:
                house_image.image.delete()


# @receiver(pre_delete, sender=HouseImage)
# def remove_file_from_storage(sender, instance, **kwargs):
#     if instance.image:
#         instance.image.delete()
