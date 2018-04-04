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

    room_type = models.CharField(
        verbose_name='숙소 타입',
        help_text='숙소를 선택 하세요. (기본값은 주택)',

        max_length=2,
        choices=ROOM_TYPE_CHOICES,
        default=ROOM_TYPE_HOUSING
    )
    name = models.CharField(
        verbose_name='숙소 이름',
        help_text='숙소의 이름을 입력하세요. (100자)',

        max_length=100,
    )
    description = models.TextField(
        verbose_name='숙소 설명',
        help_text='숙소를 설명 하세요. (blank/null 가능)',

        blank=True,
        null=True,
    )
    address = models.CharField(
        verbose_name='주소지',
        help_text='주소지를 입력 하세요 (200자)',

        max_length=200,
    )

    room = models.PositiveSmallIntegerField(
        verbose_name='방 수',
        help_text='방 수를 입력 하세요. (기본값은 1개)',

        default=1,
    )
    bed = models.PositiveSmallIntegerField(
        verbose_name='침대 수',
        help_text='침대 수를 입력 하세요. (기본값은 0개)',

        default=0,
    )
    bathroom = models.PositiveSmallIntegerField(
        verbose_name='욕실 수',
        help_text='욕실 수를 입력 하세요. (기본값은 1개)',

        default=1,
    )

    personnel = models.PositiveSmallIntegerField(
        verbose_name='숙박 인원',
        help_text='숙박 인원 입력 하세요. (기본값은 1명)',

        default=1,
    )

    amenities = models.ManyToManyField(
        'Amenities',

        verbose_name='편의 물품',
        help_text='편의 물품의 종류를 선택하세요. (blank/null 가능)',

        related_name='houses_with_amenities',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    facilities = models.ManyToManyField(
        'Facilities',

        verbose_name='편의 시설',
        help_text='편의 시설을 선택하세요. (blank/null 가능)',

        related_name='Nearby_facilities',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    minimum_check_in_duration = models.PositiveSmallIntegerField(
        verbose_name='최소 체크인 기간',
        help_text='체크인 할 수 있는 최소 기간을 입력 하세요. (기본값은 1)',

        default=1,
    )
    maximum_check_in_duration = models.PositiveSmallIntegerField(
        verbose_name='최대 체크인 기간',
        help_text='체크인 할 수 있는 최대 기간을 입력 하세요. (기본값은 3)',

        default=3,
    )

    start_day_for_break = models.DateField(
        verbose_name='쉬는 시작 날짜',
        help_text='날짜로 입력 가능 합니다.',

        blank=True,
        null=True,
    )
    end_day_for_break = models.DateField(
        verbose_name='쉬는 마지막 날짜',
        help_text='날짜로 입력 가능 합니다.',

        blank=True,
        null=True,
    )
    possible_check_in_date_start = models.DateField(
        verbose_name='체크인이 가능한 시작날',
        help_text='날짜로 입력 가능 합니다.',

        blank=True,
        null=True,
    )
    possible_check_in_date_end = models.DateField(
        verbose_name='체크인이 가능한 마지막날',
        help_text='날짜로 입력 가능 합니다.',

        blank=True,
        null=True,
    )


class HouseImage(models.Model):
    image = models.ImageField('숙소 이미지', upload_to='house')

    house = models.ForeignKey(
        House,

        verbose_name='숙소',
        help_text='이미지와 연결된 숙소를 저장합니다.',

        related_name='houses_with_image',
    )

class Amenities(models.Model):
    name = models.CharField(
        verbose_name='편의 물품',
        help_text='100자 까지의 물건의 이름을 저장 합니다.',

        max_length=100,
        unique=True,
    )

class Facilities(models.Model)
    name = models.CharField(
        verbose_name='편의 시설',
        help_text='100자 까지의 시설의 이름을 저장 합니다.',

        max_length=100,
        unique=True,
    )