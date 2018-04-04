from django.conf import settings
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
        blank=True,
    )

    facilities = models.ManyToManyField(
        'Facilities',

        verbose_name='편의 시설',
        help_text='편의 시설을 선택하세요. (blank/null 가능)',

        related_name='Nearby_facilities',
        blank=True,
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
    maximum_check_in_range = models.PositiveSmallIntegerField(
        verbose_name='가능한 Day값',
        help_text='오늘을 기준으로 체크인이 가능한 일 수 적어주세요 (기본값은 90)',

        # 90일
        default=90,
    )

    DEFAULT_FEE_FOR_DAY = 100000
    fee_for_day = models.PositiveSmallIntegerField(
        verbose_name='하루 요금',
        help_text='하루 요금을 적어 주세요. 기본값(100,000)',

        default=DEFAULT_FEE_FOR_DAY,
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

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,

        verbose_name='판매자',
        help_text='숙소를 등록하는 판매자 입니다.',

        related_name='houses_with_host',
        on_delete=models.CASCADE,
    )

    guest = models.ManyToManyField(
        settings.AUTH_USER_MODEL,

        verbose_name='편의 시설',
        help_text='편의 시설을 선택하세요. (blank/null 가능)',

        related_name='Nearby_facilities',
        blank=True,
    )


class HouseLocation(models.Model):
    address = models.CharField(
        verbose_name='주소지',
        help_text='주소지를 입력 하세요 (200자)',

        max_length=200,
    )

    latitude = models.FloatField(

    )
    longitude = models.FloatField(

    )


class HouseImage(models.Model):
    """
    HouseImage모델은  House모델을 참조 하며
    House모델이 지워지면 연결된 HouseImage모델도 지워 진다.
    """
    image = models.ImageField('숙소 이미지', upload_to='house')

    house = models.ForeignKey(
        House,

        verbose_name='숙소',
        help_text='이미지와 연결된 숙소를 저장합니다.',

        related_name='houses_with_image',
        on_delete=models.CASCADE,
    )


class Amenities(models.Model):
    """
    House와 연결된 편의 물품
    """
    name = models.CharField(
        verbose_name='편의 물품',
        help_text='100자 까지의 물건의 이름을 저장 합니다.',

        max_length=100,
        unique=True,
    )


class Facilities(models.Model):
    """
    House와 연결된 편의 시설
    """
    name = models.CharField(
        verbose_name='편의 시설',
        help_text='100자 까지의 시설의 이름을 저장 합니다.',

        max_length=100,
        unique=True,
    )


class RelationWithHouseAndGuest(models.Model):
    """
    Houst와 User의 관계 테이블
    혹시 추가적인 데이터 삽입을 고려하여
    중개 모델로 만듬.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,

        verbose_name='게스트',
        help_text='숙소를 예약한 게스트 입니다.',

        on_delete=models.CASCADE,
    )
    house = models.ForeignKey(
        House,

        verbose_name='숙소',
        help_text='게스트가 예약한 숙소 입니다.',

        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (
            ('house', 'user'),
        )
