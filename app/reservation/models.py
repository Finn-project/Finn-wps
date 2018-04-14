from django.conf import settings
from django.db import models

from house.models import House

__all__ = (
    'Reservation',
)


class Reservation(models.Model):
    check_in_date = models.DateField(unique=True)
    check_out_date = models.DateField(unique=True)
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

    RESERVATION_FINISHED = 'FI'
    RESERVATION_ONGOING = 'ON'
    RESERVATION_ACCEPTED_BY_HOST = 'AC'
    RESERVATION_DENIED_BY_HOST = 'DE'
    RESERVATION_CANCELED_BY_HOST = 'CH'
    RESERVATION_CANCELED_BY_GUEST = 'CG'
    RESERVATION_REQUEST_CANCELED_BY_GUEST = 'RC'
    RESERVATION_REQUESTED_BY_GUEST = 'RE'

    RESERVATION_STATUS_CHOICES = (
        (RESERVATION_FINISHED, '숙박종료됨'),
        (RESERVATION_ONGOING, '현재숙박중'),
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

    class Meta:
        verbose_name_plural = '예약'

    def __str__(self):
        return '{} 님의 예약 (기간: {} ~ {}) | 호스트: {}'.format(
            self.guest,
            self.check_in_date,
            self.check_out_date,
            self.house.host,
        )
