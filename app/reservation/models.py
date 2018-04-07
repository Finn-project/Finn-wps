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
    bank_account = models.CharField(max_length=30)

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

    def __str__(self):
        return '{} 님의 예약 (기간: {} ~ {}) | 호스트: {}'.format(
            self.guest,
            self.check_in_date,
            self.check_out_date,
            self.house.host,
        )
