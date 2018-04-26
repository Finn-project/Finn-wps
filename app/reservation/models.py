import datetime
from django.conf import settings
from django.db import models
from django.utils import timezone

from house.models import House

__all__ = (
    'Reservation',
)


class Reservation(models.Model):
    check_in_date = models.DateField(blank=False)
    check_out_date = models.DateField(blank=False)
    guest_num = models.PositiveSmallIntegerField(blank=True, default=1)
    # bank_account = models.CharField(max_length=30)

    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
    )
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)

    PAYMENT_TYPE_DEPOSIT = 'DE'
    # PAYMENT_TYPE_CREDITCARD = 'CR'
    # PAYMENT_TYPE_PAYPAL = 'PA'

    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE_DEPOSIT, '무통장입금'),
        # (PAYMENT_TYPE_CREDITCARD, '신용카드'),
        # (PAYMENT_TYPE_PAYPAL, '페이팔')
    )
    payment_type = models.CharField(max_length=2, choices=PAYMENT_TYPE_CHOICES, default=PAYMENT_TYPE_DEPOSIT)

    # (message 구현여부에 따라 결정) 예약과정에서 호스트에게 보내는 메시지
    # message_to_host = models.TextField(max_length=300)

    RESERVATION_ACCEPTED_BY_HOST = 'AC'
    RESERVATION_DENIED_BY_HOST = 'DE'
    RESERVATION_CANCELED_BY_HOST = 'CH'
    RESERVATION_CANCELED_BY_GUEST = 'CG'
    RESERVATION_REQUEST_CANCELED_BY_GUEST = 'RC'
    RESERVATION_REQUESTED_BY_GUEST = 'RE'

    RESERVATION_STATUS_CHOICES = (
        (RESERVATION_ACCEPTED_BY_HOST, '예약수락됨'),
        (RESERVATION_DENIED_BY_HOST, '예약거절됨'),
        (RESERVATION_CANCELED_BY_HOST, '예약취소됨(호스트)'),
        (RESERVATION_CANCELED_BY_GUEST, '예약취소됨(게스트)'),
        (RESERVATION_REQUEST_CANCELED_BY_GUEST, '예약요청취소됨'),
        (RESERVATION_REQUESTED_BY_GUEST, '예약요청됨'),
    )

    reservation_status = models.CharField(
        max_length=2,
        choices=RESERVATION_STATUS_CHOICES,
        default=RESERVATION_REQUESTED_BY_GUEST
    )

    # reservation_current_state = models.CharField(max_length=2, blank=True)


    @property
    def reservation_current_state(self):

        now = timezone.now()
        now_date = now.strftime('%Y-%m-%d')
        # print(now_date)
        # print(type(now_date))

        # print(now.day)
        # print(type(now.day))
        #
        # now = timezone.now()
        # now2 = timezone.timedelta()
        # print(now)
        # print(now2)
        #
        # print(type(self.check_in_date))
        # print(type(datetime.date(now.year, now.month, now.day)))
        # print(datetime.date(now.year, now.month, now.day))

        # if self.check_in_date > now_date:
        date_now = datetime.date(now.year, now.month, now.day)
        # check_in_date field는 datetime.date type이라서
        # 2018-04-19 형태로 된 값과 비교를 해야되서
        # datetime.date를 써야되는데 현재 시점의 datetime.date를
        # 구할 방법이 없어서 위와 같이 now.year를 활용함.
        if self.check_in_date > date_now:
            return 'BE'
            # Before reservation
        elif self.check_out_date < date_now:
            return 'AF'
            # After reservation
        else:
            return 'ON'
            # Ongoing reservation

    class Meta:
        verbose_name_plural = '예약'

    def __str__(self):
        return '{} {}(pk|{}) 님의 예약 (기간: {} ~ {}) | 호스트: {}(pk|{})'.format(
            [self.pk],
            self.guest.username,
            self.guest.pk,
            self.check_in_date,
            self.check_out_date,
            self.house.host.username,
            self.house.host.pk,
        )
